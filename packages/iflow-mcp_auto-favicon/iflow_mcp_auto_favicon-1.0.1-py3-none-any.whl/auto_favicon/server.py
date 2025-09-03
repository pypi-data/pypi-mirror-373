#!/usr/bin/env python3
"""
MCP FastMCP Server for Automatic Favicon Generation

This server provides tools to generate favicons from PNG images or URLs.
It creates a complete favicon set including various sizes and a manifest.json file.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from PIL import Image
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="favicon-generator")

FAVICON_SIZES = [16, 32, 48, 64, 128, 256]
ICO_SIZES = [16, 32, 48]
APPLE_SIZES = [180, 152, 144, 120, 114, 76, 72, 60, 57]


def validate_absolute_path(path: str, path_type: str) -> Path:
    """Validate that a path is absolute and exists (for files) or can be created (for directories)."""
    path_obj = Path(path)
    
    if not path_obj.is_absolute():
        raise ValueError(f"{path_type} must be an absolute path: {path}")
    
    return path_obj


def create_favicon_set(image_data: bytes, output_dir: str) -> Dict[str, Any]:
    """Create a complete favicon set from image data."""
    # Write image data to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_file.write(image_data)
        temp_file.flush()
        temp_path = temp_file.name

    try:
        with Image.open(temp_path) as img:
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            generated_files = []

            # Generate PNG favicons
            for size in FAVICON_SIZES:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                filename = f"favicon-{size}x{size}.png"
                filepath = output_path / filename
                resized.save(filepath, "PNG")
                generated_files.append(str(filepath))

            # Generate ICO file
            ico_images = [img.resize((size, size), Image.Resampling.LANCZOS) for size in ICO_SIZES]
            ico_path = output_path / "favicon.ico"
            ico_images[0].save(ico_path, format='ICO', sizes=[(size, size) for size in ICO_SIZES])
            generated_files.append(str(ico_path))

            # Generate Apple touch icons
            for size in APPLE_SIZES:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                filename = f"apple-touch-icon-{size}x{size}.png"
                filepath = output_path / filename
                resized.save(filepath, "PNG")
                generated_files.append(str(filepath))

            # Generate manifest.json
            manifest = {
                "name": "Favicon App",
                "short_name": "Favicon",
                "description": "Generated favicon application",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#000000",
                "icons": [
                    {
                        "src": f"favicon-{size}x{size}.png",
                        "sizes": f"{size}x{size}",
                        "type": "image/png"
                    } for size in FAVICON_SIZES
                ]
            }
            manifest_path = output_path / "manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            generated_files.append(str(manifest_path))

            return {
                "generated_files": generated_files,
                "manifest": manifest,
                "output_directory": str(output_path)
            }
    finally:
        os.unlink(temp_path)


@mcp.tool()
async def generate_favicon_from_png(image_path: str, output_path: str) -> str:
    """
    Generate a complete favicon set from a PNG image file.

    Args:
        image_path: Absolute path to the PNG image file.
        output_path: Absolute path to the directory where favicon files will be generated.
    Returns:
        A message describing the generated files and output directory.
    """
    try:
        # Validate absolute paths
        image_path_obj = validate_absolute_path(image_path, "image_path")
        output_path_obj = validate_absolute_path(output_path, "output_path")
        
        # Check if image file exists
        if not image_path_obj.exists():
            return f"Error: Image file does not exist: {image_path}"
        
        if not image_path_obj.is_file():
            return f"Error: Path is not a file: {image_path}"
        
        # Check if output directory can be created
        try:
            output_path_obj.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return f"Error: Cannot create output directory {output_path}: {str(e)}"
        
        with open(image_path_obj, 'rb') as f:
            image_data = f.read()
        result = create_favicon_set(image_data, str(output_path_obj))
        return (
            f"Successfully generated favicon set!\n\n"
            f"Output directory: {result['output_directory']}\n"
            f"Generated files:\n" + "\n".join(f"- {f}" for f in result['generated_files'])
        )
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error generating favicon: {str(e)}"


@mcp.tool()
async def generate_favicon_from_url(image_url: str, output_path: str) -> str:
    """
    Download an image from a URL and generate a complete favicon set.

    Args:
        image_url: URL of the image to download.
        output_path: Absolute path to the directory where favicon files will be generated.
    Returns:
        A message describing the generated files and output directory.
    """
    try:
        # Validate absolute path for output directory
        output_path_obj = validate_absolute_path(output_path, "output_path")
        
        # Check if output directory can be created
        try:
            output_path_obj.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return f"Error: Cannot create output directory {output_path}: {str(e)}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                response.raise_for_status()
                image_data = await response.read()
        result = create_favicon_set(image_data, str(output_path_obj))
        return (
            f"Successfully downloaded image from {image_url} and generated favicon set!\n\n"
            f"Output directory: {result['output_directory']}\n"
            f"Generated files:\n" + "\n".join(f"- {f}" for f in result['generated_files'])
        )
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error generating favicon from URL: {str(e)}"


def main():
    """MCP Auto Favicon Server - Automatic favicon generation functionality for MCP"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate favicons from PNG images or URLs"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="./favicons",
        help="Default output directory for generated favicons"
    )

    args = parser.parse_args()
    
    # Initialize and run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main() 