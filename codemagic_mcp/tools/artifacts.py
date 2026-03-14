from typing import Any

from mcp.server.fastmcp import FastMCP

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_artifact_url(secure_filename: str) -> Any:
        """Get the download URL for a build artifact.

        Args:
            secure_filename: The secure filename of the artifact (from build results).
        """
        async with CodemagicClient() as client:
            return await client.get_artifact_url(secure_filename)

    @mcp.tool()
    async def create_artifact_public_url(
        secure_filename: str, expires_at: int
    ) -> Any:
        """Create a time-limited public URL for a build artifact.

        Args:
            secure_filename: The secure filename of the artifact (from build results).
            expires_at: Expiry time as a UNIX timestamp (seconds since epoch).
        """
        async with CodemagicClient() as client:
            return await client.create_artifact_public_url(secure_filename, expires_at)
