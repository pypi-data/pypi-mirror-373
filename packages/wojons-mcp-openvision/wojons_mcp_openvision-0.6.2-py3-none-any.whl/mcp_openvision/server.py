"""
OpenVision MCP Server

A simple MCP server that provides image analysis capabilities using OpenRouter.
"""

import base64
import json
import sys
import asyncio
import os
from pathlib import Path
import re
import mimetypes
from typing import Dict, List, Optional, Any, Union, Tuple
from urllib.parse import urlparse

import requests
from mcp.server.fastmcp import FastMCP
from mcp import types

from .config import VisionModel, get_api_key, get_default_model
from .exceptions import OpenRouterError, ConfigurationError

# Initialize FastMCP with dependencies
mcp = FastMCP(
    "OpenVision",
    instructions="Vision analysis tool for images using OpenRouter",
)

# Ensure mimetypes are initialized
mimetypes.init()


def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image data to base64."""
    return base64.b64encode(image_data).decode("utf-8")


def get_mime_type(file_path: str, image_data: Optional[bytes] = None) -> str:
    """
    Determine MIME type from file extension or image data.

    Args:
        file_path: Path or URL to the image
        image_data: Optional raw image data to check if path doesn't provide mime type

    Returns:
        MIME type as a string (defaults to image/jpeg if cannot be determined)
    """
    # First try to get mime type from file extension
    mime_type, _ = mimetypes.guess_type(file_path)

    if mime_type and mime_type.startswith("image/"):
        return mime_type

    # Fallback to examining file headers if we have image data
    if image_data:
        # Check for PNG signature
        if image_data.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        # Check for JPEG signature
        elif image_data.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        # Check for WebP signature
        elif image_data.startswith(b"RIFF") and b"WEBP" in image_data[0:12]:
            return "image/webp"

    # Default to JPEG if we couldn't determine the type
    return "image/jpeg"


def is_url(string: str) -> bool:
    """
    Check if the provided string is a URL.

    Args:
        string: The string to check

    Returns:
        True if the string is a URL, False otherwise
    """
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_base64(string: str) -> bool:
    """
    Check if the provided string is base64-encoded.

    Args:
        string: The string to check

    Returns:
        True if the string appears to be base64-encoded, False otherwise
    """
    # Remove base64 URL prefix if present
    if string.startswith("data:image"):
        # Extract the actual base64 content
        pattern = r"base64,(.*)"
        match = re.search(pattern, string)
        if match:
            string = match.group(1)

    # Check if string is base64
    try:
        # Check if the string matches base64 pattern
        if not isinstance(string, str):
            return False

        # Check if the string follows base64 format (may have padding)
        # This regex allows for the standard base64 character set and optional padding
        if not re.match(r"^[A-Za-z0-9+/]*={0,2}$", string):
            return False

        # If it's too short, it's probably not base64
        if len(string) < 4:  # Minimum meaningful base64 is 4 chars
            return False

        # Try decoding - this will raise an exception if not valid base64
        decoded = base64.b64decode(string)
        # If we can decode it, it's likely base64
        return True
    except Exception:
        # If any exception occurs during decoding, it's not valid base64
        return False


def extract_mime_type_from_data_url(data_url: str) -> str:
    """
    Extract MIME type from a data URL.

    Args:
        data_url: The data URL string

    Returns:
        The MIME type or 'image/jpeg' if not found
    """
    pattern = r"data:(image/[^;]+)"
    match = re.search(pattern, data_url)
    if match:
        return match.group(1)
    return "image/jpeg"


def load_image_from_url(url: str) -> str:
    """
    Download an image from a URL and convert it to base64.

    Args:
        url: The URL of the image

    Returns:
        Tuple containing (base64_encoded_image, mime_type)

    Raises:
        Exception: If the image cannot be downloaded
    """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses

        # Explicitly handle non-200 responses (helps when raise_for_status is mocked)
        if response.status_code != 200:
            raise Exception(f"Failed to download image from URL: {url}, error: HTTP {response.status_code}")

        # Get content type from headers or guess from URL
        content_type = response.headers.get("Content-Type")
        if not content_type or not content_type.startswith("image/"):
            content_type = get_mime_type(url, response.content)

        return encode_image_to_base64(response.content)
    except requests.RequestException as e:
        raise Exception(f"Failed to download image from URL: {url}, error: {str(e)}")


def load_image_from_path(
    path: str, project_root: Optional[str] = None
) -> str:
    """
    Load an image from a local file path and convert it to base64.

    Args:
        path: The path to the image file
        project_root: Optional root directory to resolve relative paths against

    Returns:
        Tuple containing (base64_encoded_image, mime_type)

    Raises:
        FileNotFoundError: If the image file does not exist
        PermissionError: If the image file cannot be read
    """
    # Create a Path object from the input path
    file_path = Path(path)

    # If the path is absolute, use it directly
    if file_path.is_absolute():
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found at absolute path: {path}")
        try:
            with open(file_path, "rb") as f:
                image_data = f.read()
                mime_type = get_mime_type(str(file_path), image_data)
                return encode_image_to_base64(image_data)
        except PermissionError:
            raise PermissionError(
                f"Permission denied when trying to read image file at: {path}"
            )
        except Exception as e:
            raise Exception(f"Error reading image file at: {path}, error: {str(e)}")

    # For relative paths, we need to handle differently
    paths_to_try = [file_path]  # Always try the direct path first

    # If project_root is provided, try resolving against it
    if project_root:
        # Normalize path regardless of OS
        root_path = Path(project_root)
        if root_path.exists() and root_path.is_dir():
            paths_to_try.append(root_path / path)

    # Try each path
    for p in paths_to_try:
        if p.exists():
            try:
                with open(p, "rb") as f:
                    image_data = f.read()
                    mime_type = get_mime_type(str(p), image_data)
                    return encode_image_to_base64(image_data)
            except PermissionError:
                # Continue to try other paths if permission error
                continue
            except Exception as e:
                raise Exception(f"Error reading image file at: {p}, error: {str(e)}")

    # If we get here, the file wasn't found
    if project_root:
        raise FileNotFoundError(
            f"Image file not found: {path} (tried directly and under project root: {project_root})"
        )
    else:
        raise FileNotFoundError(
            f"Image file not found: {path} (relative path used without specifying project_root)"
        )


def process_image_input(
    image: str, project_root: Optional[str] = None
) -> str:
    """
    Process the image input, which can be a URL, file path, or base64-encoded data.

    Args:
        image: The image input as a URL, file path, or base64-encoded data
        project_root: Optional root directory to resolve relative paths against

    Returns:
        Tuple containing (base64_encoded_image, mime_type)

    Raises:
        ValueError: If the image cannot be processed
    """
    # Check if the image is already a data URL with base64
    if image.startswith("data:image"):
        mime_type = extract_mime_type_from_data_url(image)
        pattern = r"base64,(.*)"
        match = re.search(pattern, image)
        if match:
            return match.group(1)

    # Check if the image is just base64-encoded (without data URL prefix)
    if is_base64(image):
        # For plain base64, we'll need to guess the mime type
        return image  # Default to jpeg for plain base64 when determining mime later

    # Check if the image is a URL
    if is_url(image):
        return load_image_from_url(image)

    # Check if the image is a file path
    try:
        return load_image_from_path(image, project_root)
    except (FileNotFoundError, PermissionError) as e:
        raise ValueError(
            f"Invalid image input: {str(e)}. "
            f"Image must be a base64-encoded string, a URL, or a valid file path."
        )
    except Exception as e:
        raise ValueError(f"Error processing image: {str(e)}")


@mcp.tool()
async def image_analysis(
    image: str,
    query: str = "Describe this image in detail",
    system_prompt: str = "You are an expert vision analyzer with exceptional attention to detail. Your purpose is to provide accurate, comprehensive descriptions of images that help AI agents understand visual content they cannot directly perceive. Focus on describing all relevant elements in the image - objects, people, text, colors, spatial relationships, actions, and context. Be precise but concise, organizing information from most to least important. Avoid making assumptions beyond what's visible and clearly indicate any uncertainty. When text appears in images, transcribe it verbatim within quotes. Respond only with factual descriptions without subjective judgments or creative embellishments. Your descriptions should enable an agent to make informed decisions based solely on your analysis.",
    model: Optional[str] = None,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    top_p: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    project_root: Optional[str] = None,
) -> str:
    """
    Analyze an image using OpenRouter's vision capabilities.

    This tool allows you to send an image to OpenRouter's vision models for analysis.
    You provide a query to guide the analysis and can optionally customize the system prompt
    for more control over the model's behavior.

    Args:
        image: The image as a base64-encoded string, URL, or local file path
        query: Text prompt to guide the image analysis. For best results, provide context
               about why you're analyzing the image and what specific information you need.
               Including details about your purpose and required focus areas leads to more
               relevant and useful responses.
        system_prompt: Instructions for the model defining its role and behavior
        model: The vision model to use (defaults to the value set by OPENROUTER_DEFAULT_MODEL)
        max_tokens: Maximum number of tokens in the response (100-4000)
        temperature: Temperature parameter for generation (0.0-1.0)
        top_p: Optional nucleus sampling parameter (0.0-1.0)
        presence_penalty: Optional penalty for new tokens based on presence in text so far (0.0-2.0)
        frequency_penalty: Optional penalty for new tokens based on frequency in text so far (0.0-2.0)
        project_root: Optional root directory to resolve relative image paths against

    Returns:
        The analysis result as text

    Examples:
        Basic usage with a file path:
            image_analysis(image="path/to/image.jpg", query="Describe this image in detail")

        Basic usage with an image URL:
            image_analysis(image="https://example.com/image.jpg", query="Describe this image in detail")

        Basic usage with a relative path and project root:
            image_analysis(image="examples/image.jpg", project_root="/path/to/project", query="Describe this image in detail")

        Usage with a detailed contextual query:
            image_analysis(
                image="path/to/image.jpg",
                query="Analyze this product packaging design for a fitness supplement. Identify all nutritional claims,
                      certifications, and health icons. Assess the visual hierarchy and how the key selling points
                      are communicated. This is for a competitive analysis project."
            )

        Usage with custom system prompt:
            image_analysis(
                image="path/to/image.jpg",
                query="What objects can you see in this image?",
                system_prompt="You are an expert at identifying objects in images. Focus on listing all visible objects."
            )
    """
    # Validate parameter constraints
    if max_tokens < 100 or max_tokens > 8000:
        raise ValueError("max_tokens must be between 100 and 4000")

    if temperature < 0.0 or temperature > 1.0:
        raise ValueError("temperature must be between 0.0 and 1.0")

    if top_p is not None and (top_p < 0.0 or top_p > 1.0):
        raise ValueError("top_p must be between 0.0 and 1.0")

    if presence_penalty is not None and (
        presence_penalty < 0.0 or presence_penalty > 2.0
    ):
        raise ValueError("presence_penalty must be between 0.0 and 2.0")

    if frequency_penalty is not None and (
        frequency_penalty < 0.0 or frequency_penalty > 2.0
    ):
        raise ValueError("frequency_penalty must be between 0.0 and 2.0")

    # Process the image input (URL, file path, or base64)
    try:
        base64_image = process_image_input(image, project_root)
        # Derive MIME type based on input
        if image.startswith("data:image"):
            mime_type = extract_mime_type_from_data_url(image)
        elif is_url(image):
            mime_type = get_mime_type(image)
        elif is_base64(image):
            mime_type = "image/jpeg"
        else:
            mime_type = get_mime_type(image)
        print(f"Image processed successfully. Detected MIME type: {mime_type}")
    except Exception as e:
        # Provide more helpful error message with examples
        error_msg = f"Failed to process image: {str(e)}\n\n"
        error_msg += "Make sure your image is specified correctly:\n"
        error_msg += "- For file paths, try providing the full absolute path\n"
        error_msg += "- For relative paths, specify the project_root parameter\n"
        error_msg += "- For URLs, ensure they are publicly accessible\n"
        error_msg += "- For base64, ensure the encoding is correct\n\n"
        error_msg += "Examples:\n"
        error_msg += 'image_analysis(image="/full/path/to/image.jpg", query="Describe this image")\n'
        error_msg += 'image_analysis(image="relative/path/image.jpg", project_root="/root/dir", query="What\'s in this image?")\n'
        error_msg += 'image_analysis(image="https://example.com/image.jpg", query="Analyze this image")'
        raise ValueError(error_msg)

    # If no model specified, use the default model from environment or fallback
    if model is None:
        selected_model = get_default_model()
        if isinstance(selected_model, VisionModel):
            model_value = selected_model.value
        else:
            # Handle custom model string
            model_value = selected_model
    else:
        # Allow any custom model string directly from the parameter
        model_value = model

    # Get API key
    try:
        api_key = get_api_key()
    except ConfigurationError as e:
        raise

    print(f"Processing image with model: {model_value}")

    # Prepare messages for the OpenRouter request
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": query},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                },
            ],
        },
    ]

    # Prepare OpenRouter request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/modelcontextprotocol/mcp-openvision",
        "X-Title": "MCP OpenVision",
    }

    # Start with required parameters
    payload = {
        "model": model_value,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # Add optional parameters if provided
    if top_p is not None:
        payload["top_p"] = top_p

    if presence_penalty is not None:
        payload["presence_penalty"] = presence_penalty

    if frequency_penalty is not None:
        payload["frequency_penalty"] = frequency_penalty

    print("Sending request to OpenRouter...")

    try:
        # Make the API call
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
        )

        # Check for errors
        if response.status_code != 200:
            error_msg = (
                f"Error from OpenRouter: {response.status_code} - {response.text}"
            )
            print(error_msg)
            raise OpenRouterError(response.status_code, response.text)

        # Parse the response
        result = response.json()
        analysis = result["choices"][0]["message"]["content"]

        print("Analysis completed successfully")

        return analysis

    except requests.RequestException as e:
        error_msg = f"Network error when connecting to OpenRouter: {str(e)}"
        print(error_msg)
        raise OpenRouterError(0, error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Error parsing OpenRouter response: {str(e)}"
        print(error_msg)
        raise OpenRouterError(0, error_msg)


def main():
    """Run the MCP server."""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    mcp.run()
