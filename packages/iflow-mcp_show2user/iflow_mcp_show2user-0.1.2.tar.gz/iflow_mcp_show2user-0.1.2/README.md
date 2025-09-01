# MCP Show2User Server

A Model Context Protocol server for displaying reports to users in various formats.

## Features

- Display reports with title, type, content, and content_type
- Support for HTML and Markdown format types
- Support for URL and text content types
- Simple JSON output format

## Installation

```bash
cd mcp-show2user
pip install -e .
```

## Usage

Run the server:

```bash
mcp-show2user
```

## Tool

### show_report

Display a report to the user.

**Parameters:**
- `title` (string): Title of the report
- `type` (string): Report type - "html" or "md"
- `content` (string): Report content (URL or text based on content_type)
- `content_type` (string): Content type - "url" or "text"

**Example:**

```json
{
  "title": "Monthly Sales Report",
  "type": "html",
  "content": "https://example.com/report.html",
  "content_type": "url"
}
```

## License

MIT