# MCP OpenVision Quick Start Guide

This guide will help you get started with the MCP OpenVision server quickly.

## Prerequisites

- Python 3.10 or higher
- An OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
- Claude Desktop, Cursor, or another MCP client

## Installation

### Installing from PyPI (Recommended)

```bash
# Install the package globally
pip install mcp-openvision
```

This is the simplest method as it allows you to use the `uvx` command in your mcp.json configuration.

## Configuration

### Configuring in mcp.json

The primary way to configure MCP servers is through the mcp.json file, which is used by most MCP clients.

1. **Locate your mcp.json file**:

   - Cursor: `~/.cursor/mcp.json` (Linux/macOS) or `%USERPROFILE%\.cursor\mcp.json` (Windows)
   - Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)

2. **Add the OpenVision configuration**:

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

Replace `your_openrouter_api_key_here` with your actual OpenRouter API key.

3. **Save the file** and restart your MCP client.

### Environment Variables

MCP OpenVision can be configured using these environment variables in your mcp.json:

- **OPENROUTER_API_KEY** (required): Your OpenRouter API key
- **OPENROUTER_DEFAULT_MODEL** (optional): The default vision model to use

Available models include:

- "qwen/qwen2.5-vl-32b-instruct:free" (default)
- "anthropic/claude-3-5-sonnet"
- "anthropic/claude-3-opus"
- "anthropic/claude-3-sonnet"
- "openai/gpt-4o"

## Using MCP OpenVision

Once configured, you can use MCP OpenVision with prompts like:

- "Analyze this screenshot and tell me what's happening on the webpage"
- "Extract all text from this image"
- "Compare these two images and tell me the differences"
- "Detect objects in this image and give me their positions"
- "Is there a chart in this image? If so, analyze it and extract the data"

## Available Tools

MCP OpenVision provides these main tools:

- **analyze_image**: Analyzes images using different models and modes
- **extract_text_from_image**: Specialized for extracting text from images
- **compare_images**: Compares two images and describes differences
- **detect_objects**: Identifies objects in an image with confidence scores

## Image Analysis Prompts

The server also provides a prompt template system for common image analysis tasks:

- General analysis
- Detailed descriptions
- Object detection
- Text extraction
- Technical analysis
- Image comparison

You can use these prompts through the MCP client interface, typically by selecting the prompt type and providing additional instructions if needed.

## Troubleshooting

- **Server not found**: Make sure the package is installed globally
- **API key errors**: Verify your OpenRouter API key is correct
- **Server not loading**: Check that your mcp.json syntax is valid
- **Compatibility issues**: Make sure you have the latest version of the MCP SDK

For more detailed configuration options, see [MCP_CONFIG.md](MCP_CONFIG.md).
