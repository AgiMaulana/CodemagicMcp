from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_caches(app_id: str) -> Any:
        """List all build caches for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.list_caches(app_id)

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_all_caches(app_id: str) -> Any:
        """Delete all build caches for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.delete_all_caches(app_id)

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_cache(app_id: str, cache_id: str) -> Any:
        """Delete a specific build cache for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            cache_id: The cache ID to delete.
        """
        async with CodemagicClient() as client:
            return await client.delete_cache(app_id, cache_id)
