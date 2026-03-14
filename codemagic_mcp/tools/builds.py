from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_builds(
        app_id: str | None = None,
        branch: str | None = None,
        tag: str | None = None,
        limit: int = 10,
        page: int = 1,
    ) -> Any:
        """List Codemagic builds, optionally filtered by app, branch, and/or tag.

        Args:
            app_id: Optional app ID to filter builds. If omitted, returns builds across all apps.
            branch: Optional branch name to filter builds (e.g. "main").
            tag: Optional tag name to filter builds (e.g. "release_v5.57.2").
            limit: Number of builds per page (default 10).
            page: Page number to retrieve, starting from 1 (default 1).
        """
        async with CodemagicClient() as client:
            return await client.list_builds(
                app_id=app_id, branch=branch, tag=tag, limit=limit, page=page
            )

    @mcp.tool()
    async def get_build(build_id: str) -> Any:
        """Get details and status of a specific Codemagic build.

        Args:
            build_id: The Codemagic build ID.
        """
        async with CodemagicClient() as client:
            return await client.get_build(build_id)

    @mcp.tool()
    async def trigger_build(
        app_id: str,
        workflow_id: str,
        branch: str | None = None,
        tag: str | None = None,
        environment: dict[str, Any] | None = None,
        instance_type: str | None = None,
    ) -> Any:
        """Trigger a new build for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            workflow_id: The workflow ID to run.
            branch: Git branch to build (mutually exclusive with tag).
            tag: Git tag to build (mutually exclusive with branch).
            environment: Optional environment variables to override, e.g. {"variables": {"KEY": "value"}}.
            instance_type: Optional machine instance type to use for the build.
        """
        async with CodemagicClient() as client:
            return await client.trigger_build(
                app_id=app_id,
                workflow_id=workflow_id,
                branch=branch,
                tag=tag,
                environment=environment,
                instance_type=instance_type,
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def cancel_build(build_id: str) -> Any:
        """Cancel a running Codemagic build.

        Args:
            build_id: The build ID to cancel.
        """
        async with CodemagicClient() as client:
            return await client.cancel_build(build_id)

    @mcp.tool()
    async def get_build_logs(build_id: str) -> Any:
        """Get the logs for a Codemagic build.

        Args:
            build_id: The Codemagic build ID.
        """
        async with CodemagicClient() as client:
            return await client.get_build_logs(build_id)

    @mcp.tool()
    async def list_build_artifacts(build_id: str) -> Any:
        """List all artifacts produced by a Codemagic build.

        Args:
            build_id: The Codemagic build ID.
        """
        async with CodemagicClient() as client:
            return await client.list_build_artifacts(build_id)
