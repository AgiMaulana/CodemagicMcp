import asyncio
import os
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, patch

from codemagic_mcp.client import CodemagicClient
from codemagic_mcp.config import settings


class StepLogArtifactTests(unittest.TestCase):
    def setUp(self) -> None:
        self.build_id = "build123"
        self.step_id = "step456"
        self.log_text = "line 1\nline 2\nline 3\n"
        self.original_temp_dir = settings.codemagic_log_temp_dir
        self.original_ttl = settings.codemagic_log_ttl_seconds
        self.original_cleanup_interval = settings.codemagic_log_cleanup_interval_seconds
        self.original_max_total_bytes = settings.codemagic_log_max_total_bytes
        self.original_max_file_count = settings.codemagic_log_max_file_count
        self.temp_dir_context = tempfile.TemporaryDirectory()
        settings.codemagic_log_temp_dir = Path(self.temp_dir_context.name)
        settings.codemagic_log_ttl_seconds = 3600
        settings.codemagic_log_cleanup_interval_seconds = 300
        settings.codemagic_log_max_total_bytes = 1024 * 1024
        settings.codemagic_log_max_file_count = 20
        self.client = CodemagicClient()

    def tearDown(self) -> None:
        asyncio.run(self.client._client.aclose())
        settings.codemagic_log_temp_dir = self.original_temp_dir
        settings.codemagic_log_ttl_seconds = self.original_ttl
        settings.codemagic_log_cleanup_interval_seconds = self.original_cleanup_interval
        settings.codemagic_log_max_total_bytes = self.original_max_total_bytes
        settings.codemagic_log_max_file_count = self.original_max_file_count
        self.temp_dir_context.cleanup()

    def test_get_step_logs_file_returns_artifact_metadata(self) -> None:
        with patch.object(
            self.client,
            "get_step_logs",
            AsyncMock(return_value=self.log_text),
        ):
            result = asyncio.run(self.client.get_step_logs_file(self.build_id, self.step_id))

        self.assertEqual(result["status"], "available")
        self.assertEqual(
            result["artifact_id"],
            f"artifact_{self.build_id}_{self.step_id}",
        )
        self.assertTrue(Path(result["file_path"]).exists())
        self.assertEqual(result["bytes"], len(self.log_text.encode("utf-8")))
        self.assertEqual(result["line_count"], 3)

    def test_get_step_log_artifact_returns_available_when_file_exists(self) -> None:
        destination = self.client._build_log_file_path(self.build_id, self.step_id)
        self.client._write_step_log_file(destination, self.log_text)

        result = self.client.get_step_log_artifact(self.build_id, self.step_id)

        self.assertEqual(result["status"], "available")
        self.assertEqual(result["file_path"], str(destination))
        self.assertEqual(result["artifact_id"], f"artifact_{self.build_id}_{self.step_id}")
        self.assertEqual(result["line_count"], 3)

    def test_get_step_log_artifact_returns_missing_when_file_does_not_exist(self) -> None:
        result = self.client.get_step_log_artifact(self.build_id, self.step_id)

        self.assertEqual(result["status"], "missing")
        self.assertEqual(result["reason"], "not_generated_or_expired")
        self.assertEqual(result["artifact_id"], f"artifact_{self.build_id}_{self.step_id}")

    def test_expired_artifact_is_deleted_and_reported_missing(self) -> None:
        destination = self.client._build_log_file_path(self.build_id, self.step_id)
        self.client._write_step_log_file(destination, self.log_text)
        expired_mtime = (datetime.now(UTC) - timedelta(seconds=7200)).timestamp()
        os.utime(destination, (expired_mtime, expired_mtime))

        result = self.client.get_step_log_artifact(self.build_id, self.step_id)

        self.assertEqual(result["status"], "missing")
        self.assertFalse(destination.exists())

    def test_lookup_does_not_fetch_or_recreate_missing_artifact(self) -> None:
        with patch.object(
            self.client,
            "get_step_logs",
            AsyncMock(side_effect=AssertionError("should not fetch logs")),
        ):
            result = self.client.get_step_log_artifact(self.build_id, self.step_id)

        self.assertEqual(result["status"], "missing")
        self.assertFalse(self.client._build_log_file_path(self.build_id, self.step_id).exists())

    def test_expires_at_uses_file_mtime_plus_ttl(self) -> None:
        destination = self.client._build_log_file_path(self.build_id, self.step_id)
        self.client._write_step_log_file(destination, self.log_text)
        modified_at = datetime.now(UTC) - timedelta(seconds=60)
        modified_timestamp = modified_at.timestamp()
        os.utime(destination, (modified_timestamp, modified_timestamp))

        result = self.client.get_step_log_artifact(self.build_id, self.step_id)

        self.assertEqual(
            result["expires_at"],
            (modified_at + timedelta(seconds=settings.codemagic_log_ttl_seconds))
            .isoformat()
            .replace("+00:00", "Z"),
        )

    def test_cleanup_step_log_artifacts_deletes_expired_files_without_lookup(self) -> None:
        destination = self.client._build_log_file_path(self.build_id, self.step_id)
        self.client._write_step_log_file(destination, self.log_text)
        expired_mtime = (datetime.now(UTC) - timedelta(seconds=7200)).timestamp()
        os.utime(destination, (expired_mtime, expired_mtime))

        self.client.cleanup_step_log_artifacts()

        self.assertFalse(destination.exists())

    def test_cleanup_step_log_artifacts_evicts_oldest_when_file_count_limit_is_exceeded(self) -> None:
        settings.codemagic_log_max_file_count = 2
        first = self.client._build_log_file_path("build1", "step1")
        second = self.client._build_log_file_path("build2", "step2")
        third = self.client._build_log_file_path("build3", "step3")

        self.client._write_step_log_file(first, "oldest")
        self.client._write_step_log_file(second, "middle")
        self.client._write_step_log_file(third, "newest")

        now = datetime.now(UTC).timestamp()
        os.utime(first, (now - 30, now - 30))
        os.utime(second, (now - 20, now - 20))
        os.utime(third, (now - 10, now - 10))

        self.client.cleanup_step_log_artifacts()

        self.assertFalse(first.exists())
        self.assertTrue(second.exists())
        self.assertTrue(third.exists())


if __name__ == "__main__":
    unittest.main()
