from mcp.server.fastmcp import FastMCP

from codemagic_mcp.tools import register_all_tools

mcp = FastMCP(
    name="Codemagic MCP",
    instructions=(
        "Codemagic CI/CD REST API: manage builds, apps, artifacts, caches, variables, and webhooks.\n\n"
        "Destructive ops (delete_app, cancel_build, delete_cache, delete_all_caches, delete_variable, delete_webhook): confirm before executing.\n\n"
        "App ID resolution: (1) use explicit app_id; (2) use CODEMAGIC_DEFAULT_APP_ID if set (exposed as `default_app_id`); "
        "(3) call list_apps — auto-select if one result, else ask user."
    ),
)

register_all_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")
