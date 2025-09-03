# Video Format Converter MCP

A Model Context Protocol (MCP) server for video format conversion and property adjustment using FFmpeg.

## Features

- **Video Format Conversion**: Convert between different video containers (MP4, MOV, WebM, MKV, etc.)
- **Property Adjustment**: Modify resolution, codecs, bitrates, frame rates, and audio properties
- **GIF Export**: Convert video segments to high-quality GIF with palette optimization

## Installation

Install via uvx (recommended):

```bash
uvx video-format-converter-mcp
```

Or install via pip:

```bash
pip install video-format-converter-mcp
```

## Usage

Run the MCP server:

```bash
video-format-converter-mcp
```

## Requirements

- Python >=3.12
- FFmpeg installed on your system

## Tools Available

1. `convert_video_properties` - Convert video format and adjust all properties
2. `video_to_gif` - Convert video segments to high-quality GIF

## License

MIT License
