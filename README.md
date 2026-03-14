# Codemagic MCP Server

A local Python MCP server that exposes the [Codemagic CI/CD REST API](https://docs.codemagic.io/rest-api/overview/) as Claude-callable tools. Trigger builds, manage apps, download artifacts, and clear caches — all from Claude Code or Claude Desktop without leaving the chat.

## Tools

| Tool | Description |
|------|-------------|
| `list_apps` | List all applications in your Codemagic account |
| `get_app` | Get details of a specific application |
| `add_app` | Add a public repository to Codemagic |
| `add_private_app` | Add a private repository using an SSH key |
| `trigger_build` | Trigger a new build for an application |
| `cancel_build` | Cancel a running build |
| `get_artifact_url` | Get the download URL for a build artifact |
| `create_artifact_public_url` | Create a time-limited public URL for an artifact |
| `list_caches` | List all build caches for an application |
| `delete_all_caches` | Delete all build caches for an application |
| `delete_cache` | Delete a specific build cache |

## Installation

**Requirements:** Python 3.11+

```bash
git clone https://github.com/AgiMaulana/CodemagicMcp.git
cd CodemagicMcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Configuration

```bash
cp .env.example .env
# Edit .env and set your CODEMAGIC_API_KEY
```

Get your API token from [Codemagic User Settings → Integrations → Codemagic API](https://codemagic.io/settings).

## Register with Claude Code

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "codemagic": {
      "command": "/path/to/CodemagicMcp/.venv/bin/python",
      "args": ["-m", "codemagic_mcp"],
      "cwd": "/path/to/CodemagicMcp"
    }
  }
}
```

Restart Claude Code — the tools will appear in `/tools`.

## Project Structure

```
codemagic_mcp/
├── config.py        # pydantic-settings config (validates API key at startup)
├── client.py        # httpx async client, one method per endpoint
├── server.py        # FastMCP instance
└── tools/
    ├── apps.py
    ├── builds.py
    ├── artifacts.py
    └── caches.py
```

## Adding New Tools

1. Add a method to `client.py`
2. Add the tool function to the relevant `tools/*.py` file
3. That's it — `server.py` never needs to change
