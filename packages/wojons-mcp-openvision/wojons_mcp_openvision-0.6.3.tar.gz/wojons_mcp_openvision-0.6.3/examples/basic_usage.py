#!/usr/bin/env python
"""
Basic example of using the OpenVision MCP server.

This example shows how to:
1. Connect to the server
2. List available tools
3. Call the image_analysis tool with a simple prompt
"""

import asyncio
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Set up the server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "mcp_openvision"],
        env={
            # You can set environment variables here
            "OPENROUTER_API_KEY": os.environ.get("OPENROUTER_API_KEY"),
            "OPENROUTER_DEFAULT_MODEL": "qwen/qwen2.5-vl-32b-instruct:free",  # Optional: set default model
        },
    )

    print("Connecting to OpenVision MCP server...")

    # Connect to the server
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the connection
            await session.initialize()

            # List available tools
            tools_response = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools_response.tools]}")

            # Read an image file
            image_path = Path(__file__).parent / "sample_image.jpg"

            if not image_path.exists():
                print(f"Error: Sample image not found at {image_path}")
                print(
                    "Please add a sample image named 'sample_image.jpg' to the examples directory."
                )
                return

            with open(image_path, "rb") as f:
                image_data = f.read()

            print("\nAnalyzing image with basic prompt...")

            # Call the image_analysis tool with a simple query
            result = await session.call_tool(
                "image_analysis",
                {"image": {"data": image_data}, "query": "What's in this image?"},
            )

            print(f"\nResult:\n{result.content}")

            # Example with a detailed contextual query
            print("\nAnalyzing image with a detailed contextual query...")

            result = await session.call_tool(
                "image_analysis",
                {
                    "image": {"data": image_data},
                    "query": "Analyze this photograph for use in a travel blog. Identify notable landmarks, architectural styles, and cultural elements that would interest tourists. Suggest what time of day it was taken and how lighting affects the mood of the image. This will help readers understand what to expect when visiting this location."
                },
            )

            print(f"\nResult with detailed contextual query:\n{result.content}")

            # Example with custom system prompt
            print("\nAnalyzing image with custom system prompt...")

            result = await session.call_tool(
                "image_analysis",
                {
                    "image": {"data": image_data},
                    "query": "Identify all colors present in this image and explain how they work together in the composition",
                    "system_prompt": "You are a color analysis expert with deep knowledge of color theory and visual design. Focus on identifying precise color values, their relationships, emotional impacts, and practical applications in design contexts. Analyze colors using terminology from professional color systems (RGB, CMYK, HSL, etc.) when relevant."
                },
            )

            print(f"\nResult with custom system prompt:\n{result.content}")

            # Example with relative path and project_root
            print("\nAnalyzing image using a relative path with project_root...")

            # Get the current working directory to use as a project_root example
            project_root = os.getcwd()

            # Call the image_analysis tool with a relative path and project_root
            try:
                result = await session.call_tool(
                    "image_analysis",
                    {
                        "image": "examples/test_image.png",  # Relative path from project root
                        "project_root": project_root,  # Set the project root directory
                        "query": "What can you see in this image?",
                    },
                )
                print(
                    f"\nResult with relative path and project_root:\n{result.content}"
                )
            except Exception as e:
                print(f"\nError using relative path: {str(e)}")
                print(
                    "Make sure you have a file at 'examples/test_image.png' relative to the current directory."
                )

            print("\nDone!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
