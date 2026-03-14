from mcp.server.fastmcp import FastMCP

from codemagic_mcp.tools import apps, artifacts, builds, caches


def register_all_tools(mcp: FastMCP) -> None:
    apps.register(mcp)
    builds.register(mcp)
    artifacts.register(mcp)
    caches.register(mcp)
