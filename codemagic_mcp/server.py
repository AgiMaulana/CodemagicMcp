from mcp.server.fastmcp import FastMCP

from codemagic_mcp.tools import register_all_tools

mcp = FastMCP(
    name="Codemagic MCP",
    instructions=(
        "This server exposes the Codemagic CI/CD REST API as tools. "
        "Use it to manage the full build lifecycle and app configuration without leaving the chat.\n\n"
        "Available tools:\n\n"
        "Apps: list_apps, get_app, add_app, add_private_app, delete_app\n\n"
        "Builds: list_builds, get_build, trigger_build, cancel_build, get_build_logs, list_build_artifacts\n\n"
        "Artifacts: get_artifact_url, create_artifact_public_url\n\n"
        "Caches: list_caches, delete_cache, delete_all_caches\n\n"
        "Variables: list_variables, add_variable, update_variable, delete_variable\n\n"
        "Webhooks: list_webhooks, add_webhook, delete_webhook\n\n"
        "Tools marked as destructive (delete_app, cancel_build, delete_cache, delete_all_caches, "
        "delete_variable, delete_webhook) will prompt for confirmation before executing."
    ),
)

register_all_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")
