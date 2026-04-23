import asyncio
from contextlib import asynccontextmanager, suppress

from mcp.server.fastmcp import FastMCP

from codemagic_mcp.client import CodemagicClient
from codemagic_mcp.config import settings
from codemagic_mcp.tools import register_all_tools


async def _step_log_cleanup_loop() -> None:
    while True:
        async with CodemagicClient() as client:
            client.cleanup_step_log_artifacts()
        await asyncio.sleep(settings.codemagic_log_cleanup_interval_seconds)


@asynccontextmanager
async def lifespan(_: FastMCP):
    async with CodemagicClient() as client:
        client.cleanup_step_log_artifacts()

    cleanup_task = asyncio.create_task(_step_log_cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        with suppress(asyncio.CancelledError):
            await cleanup_task


mcp = FastMCP(
    name="Codemagic MCP",
    instructions=(
        "Codemagic CI/CD REST API: manage builds, apps, artifacts, caches, variables, and webhooks.\n\n"
        "Destructive ops (delete_app, cancel_build, delete_cache, delete_all_caches, delete_variable, delete_webhook): confirm before executing.\n\n"
        "App ID resolution: (1) use explicit app_id; (2) use CODEMAGIC_DEFAULT_APP_ID if set (exposed as `default_app_id`); "
        "(3) call list_apps — auto-select if one result, else ask user."
    ),
    lifespan=lifespan,
)

register_all_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")
