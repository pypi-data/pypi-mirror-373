# MCP OpenVision Configuration Guide

This guide describes how to configure MCP OpenVision in your Claude Desktop, Cursor, or other MCP client setups.

## MCP.json Configuration

The standard way to configure MCP servers is through the `mcp.json` file. This is the method used by most MCP clients, including Claude Desktop and Cursor.

### File Location

The mcp.json file is typically located at:

- Windows: `%USERPROFILE%\.cursor\mcp.json`
- macOS: `~/.cursor/mcp.json`
- Linux: `~/.cursor/mcp.json`

If you're using Claude Desktop, the file is located at:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Basic Configuration

Here's the basic format for adding MCP OpenVision to your `mcp.json` file:

```json
{
  "mcpServers": {
    "openvision": {
      "command": "uvx",
      "args": ["mcp-openvision"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_DEFAULT_MODEL": "qwen/qwen2.5-vl-32b-instruct:free"
      }
    }
  }
}
```

#### Key Components:

- **"openvision"**: The name of your MCP server (can be any unique name)
- **"command"**: The command to run (`uvx` for Python packages published to PyPI)
- **"args"**: Command arguments (in this case, the name of the package)
- **"env"**: Environment variables for configuration

### Environment Variables

MCP OpenVision supports these environment variables:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use

Valid model options include:

- "qwen/qwen2.5-vl-32b-instruct:free" (default)
- "anthropic/claude-3-5-sonnet"
- "anthropic/claude-3-opus"
- "anthropic/claude-3-sonnet"
- "openai/gpt-4o"
- Any other valid OpenRouter model ID that supports vision

### Advanced Configuration

For advanced users or development, you can configure the server to run from a local installation:

```json
{
  "mcpServers": {
    "openvision-local": {
      "command": "python",
      "args": ["-m", "mcp_openvision.server"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_DEFAULT_MODEL": "qwen/qwen2.5-vl-32b-instruct:free"
      }
    }
  }
}
```

## Enabling/Disabling Servers

Recent versions of Cursor and Claude Desktop support enabling and disabling MCP servers without removing them from the configuration:

```json
{
  "mcpServers": {
    "openvision": {
      "enabled": true,
      "command": "uvx",
      "args": ["mcp-openvision"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here",
        "OPENROUTER_DEFAULT_MODEL": "qwen/qwen2.5-vl-32b-instruct:free"
      }
    }
  }
}
```

Setting `"enabled": false` will disable the server without removing its configuration.

## Multiple MCP Servers

You can add multiple MCP servers to your configuration:

```json
{
  "mcpServers": {
    "openvision": {
      "command": "uvx",
      "args": ["mcp-openvision"],
      "env": {
        "OPENROUTER_API_KEY": "your_openrouter_api_key_here"
      }
    },
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git"]
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory"
      ]
    }
  }
}
```

## SDK Version

MCP OpenVision uses the official [Model Context Protocol SDK](https://github.com/modelcontextprotocol/python-sdk) version 1.6.0 or higher. This ensures full compatibility with the latest MCP features and improvements.

## Troubleshooting

1. **Server Not Found**: Ensure the package is installed globally if using `uvx`
2. **Permission Issues**: Check that your OpenRouter API key is correct
3. **Path Issues**: For filesystem access, make sure paths are absolute and correct for your OS
4. **SDK Compatibility**: If you encounter issues, verify you have the latest version of the MCP SDK

If you encounter issues with a specific configuration, try running the command manually in a terminal to see any error messages.
