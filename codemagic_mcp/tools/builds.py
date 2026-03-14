from typing import Any

from mcp.server.fastmcp import FastMCP

from codemagic_mcp.client import CodemagicClient


def register(mcp: FastMCP) -> None:
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

    @mcp.tool()
    async def cancel_build(build_id: str) -> Any:
        """Cancel a running Codemagic build.

        Args:
            build_id: The build ID to cancel.
        """
        async with CodemagicClient() as client:
            return await client.cancel_build(build_id)
