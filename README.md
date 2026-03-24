# EPO OPS FastMCP Server

A FastMCP server built for querying the European Patent Office (EPO) Open Patent Services (OPS) v3.2 API. This connects AI models (like Claude) with comprehensive European and worldwide patent data.

## Features
- **Published Data**: Retrieve bibliographic data, abstracts, descriptions, claims, and full-text translations.
- **Search (CQL)**: Formulate and perform robust Common Query Language (CQL) queries across EPO data.
- **Family**: Obtain the INPADOC extended patent family data for any application.
- **Legal Status**: Track INPADOC legal statuses and lifecycle events.
- **Register**: Find details on opposition, procedures, and unified patent data in the Europe registers.
- **Number Service**: Convert docdb, epodoc, and other numbering formats seamlessly.
- **PDF Downloader**: Generate direct-download URLs for the original PDF scans via the Espacenet portal.

## Prerequisites
- `uv` package manager

Ensure your `.env` contains:
```env
CONSUMER_KEY=your_epo_api_consumer_key
CONSUMER_SECRET=your_epo_api_secret_key
EPO_OPS_URL=https://ops.epo.org/3.2
```

## Running
Install dependencies and run:
```sh
uv run main.py
```

## Adding to Claude Desktop
Add it to your Claude Desktop config (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "epo_patents": {
      "command": "uv",
      "args": [
        "--directory",
        "d:/Projects 2025/EPO Fastmcp Server/epo_mcp_server",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Usage
Inside Claude, prompt for:
- "Run an EPO prior art search for..."
- "Get the claims of EP1000000A1"
- "What is the legal status for US2020123456A1?"
