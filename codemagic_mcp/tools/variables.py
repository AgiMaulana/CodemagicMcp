from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    async def list_variables(app_id: str) -> Any:
        """List all environment variables for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
        """
        async with CodemagicClient() as client:
            return await client.list_variables(app_id)

    @mcp.tool()
    async def add_variable(
        app_id: str,
        key: str,
        value: str,
        group: str,
        secure: bool = False,
    ) -> Any:
        """Add an environment variable to a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            key: The variable name.
            value: The variable value.
            group: The variable group name.
            secure: Whether the variable should be encrypted (e.g. for secrets/tokens).
        """
        async with CodemagicClient() as client:
            return await client.add_variable(
                app_id=app_id,
                key=key,
                value=value,
                group=group,
                secure=secure,
            )

    @mcp.tool()
    async def update_variable(
        app_id: str,
        variable_id: str,
        key: str,
        value: str,
        group: str,
        secure: bool = False,
    ) -> Any:
        """Update an existing environment variable for a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            variable_id: The variable ID to update.
            key: The variable name.
            value: The new variable value.
            group: The variable group name.
            secure: Whether the variable should be encrypted.
        """
        async with CodemagicClient() as client:
            return await client.update_variable(
                app_id=app_id,
                variable_id=variable_id,
                key=key,
                value=value,
                group=group,
                secure=secure,
            )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True))
    async def delete_variable(app_id: str, variable_id: str) -> Any:
        """Delete an environment variable from a Codemagic application.

        Args:
            app_id: The Codemagic application ID.
            variable_id: The variable ID to delete.
        """
        async with CodemagicClient() as client:
            return await client.delete_variable(app_id, variable_id)
