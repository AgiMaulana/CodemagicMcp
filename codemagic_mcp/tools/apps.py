from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_apps() -> Any:
        """List all applications in your Codemagic account."""
        async with CodemagicClient() as client:
            return await client.list_apps()

    @mcp.tool()
    async def get_app(app_id: str) -> Any:
        """Get details of a specific application by its ID.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.get_app(app_id)

    @mcp.tool()
    async def add_app(repository_url: str) -> Any:
        """Add a new public repository to Codemagic.

        Args:
            repository_url: The HTTPS URL of the public Git repository.
        """
        async with CodemagicClient() as client:
            return await client.add_app(repository_url)

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_app(app_id: str) -> Any:
        """Delete an application from Codemagic.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.delete_app(app_id)

    @mcp.tool()
    async def add_private_app(
        repository_url: str,
        ssh_key_data: str,
        ssh_passphrase: str | None = None,
        project_type: str | None = None,
        team_id: str | None = None,
    ) -> Any:
        """Add a new private repository to Codemagic using an SSH key.

        Args:
            repository_url: The SSH URL of the private Git repository.
            ssh_key_data: Base64-encoded SSH private key.
            ssh_passphrase: Optional passphrase for the SSH key.
            project_type: Optional project type (e.g. "flutter-app", "react-native").
            team_id: Optional team ID to add the app to.
        """
        async with CodemagicClient() as client:
            return await client.add_private_app(
                repository_url=repository_url,
                ssh_key_data=ssh_key_data,
                ssh_passphrase=ssh_passphrase,
                project_type=project_type,
                team_id=team_id,
            )
