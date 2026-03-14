from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_webhooks(app_id: str) -> Any:
        """List all webhooks configured for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.list_webhooks(app_id)

    @mcp.tool()
    async def add_webhook(app_id: str, url: str, events: list[str]) -> Any:
        """Add a webhook to a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            url: The URL to send webhook payloads to.
            events: List of events to subscribe to (e.g. ["build.finished", "build.started"]).
        """
        async with CodemagicClient() as client:
            return await client.add_webhook(app_id=app_id, url=url, events=events)

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_webhook(app_id: str, webhook_id: str) -> Any:
        """Delete a webhook from a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            webhook_id: The webhook ID to delete.
        """
        async with CodemagicClient() as client:
            return await client.delete_webhook(app_id, webhook_id)
