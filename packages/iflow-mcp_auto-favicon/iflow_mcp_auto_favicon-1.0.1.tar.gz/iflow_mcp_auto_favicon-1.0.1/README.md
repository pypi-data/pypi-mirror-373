# Auto Favicon MCP Server

An MCP (Model Context Protocol) server that automatically generates complete favicon sets from PNG images or URLs. This server creates a comprehensive set of favicon files including various sizes, Apple touch icons, and a manifest.json file.

## Features

- **PNG to Favicon**: Generate favicon sets from local PNG files
- **URL to Favicon**: Download images from URLs and generate favicon sets
- **Complete Icon Set**: Creates multiple sizes (16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
- **ICO Format**: Generates traditional favicon.ico files
- **Apple Touch Icons**: Creates Apple-specific touch icons for iOS devices
- **Web App Manifest**: Generates manifest.json for Progressive Web Apps

## Installation & Usage

### MCP Client Configuration

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "favicon-generator": {
      "command": "uvx",
      "args": ["auto-favicon"],
      "env": {}
    }
  }
}
```

## Available Tools

- `generate_favicon_from_png`: Generate favicon set from a local PNG file
- `generate_favicon_from_url`: Download image from URL and generate favicon set

## Requirements

- Python 3.12+
- uv package manager
