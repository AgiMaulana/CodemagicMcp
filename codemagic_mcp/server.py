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
        "delete_variable, delete_webhook) will prompt for confirmation before executing.\n\n"
        "App ID resolution — when a tool requires an app_id, resolve it in this order:\n"
        "1. Use the app_id explicitly provided by the user.\n"
        "2. If not provided, check whether CODEMAGIC_DEFAULT_APP_ID is configured "
        "(exposed as `default_app_id` on the client); use it silently if set.\n"
        "3. If neither is available, call list_apps to retrieve the available apps. "
        "If only one app exists, use it automatically. "
        "If multiple apps exist, present the list to the user and ask which one to use."
    ),
)

register_all_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")
