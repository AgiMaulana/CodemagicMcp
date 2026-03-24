# Codemagic MCP Server

[![MCP Registry](https://img.shields.io/badge/MCP_Registry-listed-blue)](https://registry.modelcontextprotocol.io/servers/io.github.AgiMaulana/CodemagicMcp)

A local Python MCP server that exposes the [Codemagic CI/CD REST API](https://docs.codemagic.io/rest-api/overview/) as Claude-callable tools. Trigger builds, manage apps, download artifacts, and clear caches — all from Claude Code or Claude Desktop without leaving the chat.

[![Codemagic MCP server](https://glama.ai/mcp/servers/AgiMaulana/CodemagicMcp/badges/card.svg)](https://glama.ai/mcp/servers/AgiMaulana/CodemagicMcp)

## Tools

### Apps
| Tool | Description |
|------|-------------|
| `list_apps` | List all applications in your Codemagic account |
| `get_app` | Get details of a specific application |
| `add_app` | Add a public repository to Codemagic |
| `add_private_app` | Add a private repository using an SSH key |
| `delete_app` ⚠️ | Delete an application from Codemagic |

### Builds
| Tool | Description |
|------|-------------|
| `list_builds` | List builds, optionally filtered by app |
| `get_build` | Get build details with step count summary; pass `include_steps=True` for full step list |
| `trigger_build` | Trigger a new build for an application |
| `cancel_build` ⚠️ | Cancel a running build |
| `get_build_logs` | Get a step-by-step status summary of a build (filterable by status) |
| `get_step_logs` | Get raw logs for a specific build step by step ID |
| `list_build_artifacts` | List all artifacts produced by a build |

### Artifacts
| Tool | Description |
|------|-------------|
| `get_artifact_url` | Get the download URL for a build artifact |
| `create_artifact_public_url` | Create a time-limited public URL for an artifact |

### Caches
| Tool | Description |
|------|-------------|
| `list_caches` | List all build caches for an application |
| `delete_cache` ⚠️ | Delete a specific build cache |
| `delete_all_caches` ⚠️ | Delete all build caches for an application |

### Environment Variables
| Tool | Description |
|------|-------------|
| `list_variables` | List all environment variables for an application |
| `add_variable` | Add an environment variable to an application |
| `update_variable` | Update an existing environment variable |
| `delete_variable` ⚠️ | Delete an environment variable |

### Webhooks
| Tool | Description |
|------|-------------|
| `list_webhooks` | List all webhooks for an application |
| `add_webhook` | Add a webhook to an application |
| `delete_webhook` ⚠️ | Delete a webhook |

> ⚠️ These tools are marked as destructive and will prompt for confirmation before executing.

## Quick Start

The fastest way to get running with Claude Code — no separate install step needed:

```bash
# 1. Add the server (uses uvx to run it on-demand)
claude mcp add codemagic -e CODEMAGIC_API_KEY=your-api-key-here -- uvx codemagic-mcp

# 2. Restart Claude Code — tools will appear in /tools
```

That's it. See [Configuration](#configuration) for optional settings like `CODEMAGIC_DEFAULT_APP_ID`.

---

## Installation

**Requirements:** Python 3.11+

### Option 1 — uvx (recommended, no install needed)

```bash
uvx codemagic-mcp
```

### Option 2 — pip

```bash
pip install codemagic-mcp
```

### Option 3 — from source

```bash
git clone https://github.com/AgiMaulana/CodemagicMcp.git
cd CodemagicMcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Configuration

Get your API token from [Codemagic User Settings → Integrations → Codemagic API](https://codemagic.io/settings).

You can provide settings as environment variables or via a `.env` file:

```bash
# .env
CODEMAGIC_API_KEY=your-api-key-here

# Optional: set a default app so you don't have to specify it every time
CODEMAGIC_DEFAULT_APP_ID=your-app-id-here
```

### Default App ID

`CODEMAGIC_DEFAULT_APP_ID` is optional but recommended if you work primarily with one app. When set, the AI will use it automatically whenever a tool requires an `app_id` and none was specified. If it is not set, the AI will:

1. Call `list_apps` to discover available apps.
2. Use the app automatically if only one exists.
3. Present the list and ask you to choose if multiple apps are found.

## Register with Claude Code

Run the following command to add the server:

```bash
claude mcp add codemagic -- codemagic-mcp
```

Then set your API key in the MCP env config, or export it in your shell before starting Claude Code:

```bash
export CODEMAGIC_API_KEY=your-api-key-here
```

Alternatively, add it manually to `~/.claude.json`:

```json
{
  "mcpServers": {
    "codemagic": {
      "command": "codemagic-mcp",
      "env": {
        "CODEMAGIC_API_KEY": "your-api-key-here",
        "CODEMAGIC_DEFAULT_APP_ID": "your-app-id-here"
      }
    }
  }
}
```

### Using uvx (no prior installation needed)

```json
{
  "mcpServers": {
    "codemagic": {
      "command": "uvx",
      "args": ["codemagic-mcp"],
      "env": {
        "CODEMAGIC_API_KEY": "your-api-key-here",
        "CODEMAGIC_DEFAULT_APP_ID": "your-app-id-here"
      }
    }
  }
}
```

Restart Claude Code — the tools will appear in `/tools`.

## Register with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "codemagic": {
      "command": "codemagic-mcp",
      "env": {
        "CODEMAGIC_API_KEY": "your-api-key-here",
        "CODEMAGIC_DEFAULT_APP_ID": "your-app-id-here"
      }
    }
  }
}
```

Restart Claude Desktop to pick up the changes.

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
    ├── caches.py
    ├── variables.py
    └── webhooks.py
```

## Adding New Tools

1. Add a method to `client.py`
2. Add the tool function to the relevant `tools/*.py` file
3. That's it — `server.py` never needs to change