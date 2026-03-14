from mcp.server.fastmcp import FastMCP

from codemagic_mcp.tools import register_all_tools

mcp = FastMCP(
    name="Codemagic MCP",
    instructions=(
        "This server exposes the Codemagic CI/CD REST API as tools. "
        "Use it to manage apps, trigger and cancel builds, access build artifacts, "
        "and manage build caches — all without leaving the chat."
    ),
)

register_all_tools(mcp)


def main() -> None:
    mcp.run(transport="stdio")
