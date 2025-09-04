# CodeMie Assistants MCP Server

Python server implementing Model Context Protocol (MCP) for CodeMie Assistants operations.

## Features
- Chat with AI/Run CodeMie assistant

Note: The server requires authentication credentials via environment variables.

## API

### Tools

#### chat
Chat with a specific AI assistant
Inputs:
- `message (string)`: Message to send to assistant
- `conversation_id (string)`: Identifier of current conversation. It should be always passed if present in current communication thread.
- `history (array, optional)`: Previous conversation messages in format:
  [{"role": "user|assistant", "message": "text"}]

Returns generated assistant response as text

## Installation

Ensure you have `Python 3.12` or later installed.

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will
use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *codemie-mcp-assistants*.

```bash
uvx codemie-mcp-assistants
```

### Using Poetry

Alternatively you can install via Poetry:

```bash
poetry install codemie-mcp-assistants
```

After installation, you can run it as a script using:

```bash
poetry run codemie-mcp-assistants
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
"mcpServers": {
  "codemie": {
    "command": "uvx",
    "args": ["codemie-mcp-assistants"],
    "env": {
      "CODEMIE_ASSISTANT_ID": "your-assistant-id"
      "CODEMIE_USERNAME": "your-username",
      "CODEMIE_PASSWORD": "your-password"
    }
  }
}
```
</details>

<details>
<summary>Using poetry installation</summary>

```json
"mcpServers": {
  "codemie": {
    "command": "poetry",
    "args": ["run", "codemie-mcp-assistants"],
    "env": {
      "CODEMIE_ASSISTANT_ID": "your-assistant-id"
      "CODEMIE_USERNAME": "your-username",
      "CODEMIE_PASSWORD": "your-password"
    }
  }
}
```
</details>

### Environment Variables

- `CODEMIE_ASSISTANT_ID`: "AI/Run CodeMie assistant UID"

The following environment variables are required for authentication:

- `CODEMIE_USERNAME`: Your CodeMie username
- `CODEMIE_PASSWORD`: Your CodeMie password

Optional configuration:
- `CODEMIE_AUTH_CLIENT_ID`: Auth client ID (default: "codemie-sdk")
- `CODEMIE_AUTH_REALM_NAME`: Auth realm name (default: "codemie-prod")

## Build

### Make build:
```bash
make build
```
