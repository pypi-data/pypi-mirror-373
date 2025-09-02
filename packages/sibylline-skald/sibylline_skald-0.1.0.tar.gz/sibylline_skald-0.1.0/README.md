# Skald - MCP Feedback Adapter

[![PyPI version](https://badge.fury.io/py/skald.svg)](https://badge.fury.io/py/skald)
[![Python versions](https://img.shields.io/pypi/pyversions/skald.svg)](https://pypi.org/project/skald/)
[![Tests](https://github.com/sibyllinesoft/skald/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/sibyllinesoft/skald/actions)
[![Coverage](https://codecov.io/gh/sibyllinesoft/skald/branch/main/graph/badge.svg)](https://codecov.io/gh/sibyllinesoft/skald)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> *"A storyteller for your tools' performance, letting them speak back through AI agents when they shine or stumble."*

Skald is an in-process adapter library for Python MCP servers that enables structured feedback collection on tool usefulness, clarity, and fit from AI agents.

## Features

- **Transparent Tool Wrapping**: Drop-in wrapper that intercepts MCP tool calls and adds trace IDs with metrics collection
- **Structured Feedback Collection**: New `feedback.report` tool with strict JSON schema validation
- **Smart Feedback Invitations**: Automatically invites feedback based on errors, latency, and output size
- **Opt-out Controls**: Decorator and context manager for suppressing feedback collection
- **Multiple Storage Backends**: SQLite default with optional Parquet export and data redaction
- **Multiple Transports**: Support for stdio, TCP, and Unix socket transports

## Installation

```bash
pip install skald
```

## Quick Start

### Basic Usage

```python
import skald
from your_mcp_server import YourMCPServer

# Wrap your existing MCP server
upstream = YourMCPServer()
survey = skald.SurveyingProxy(
    upstream=upstream,
    store="sqlite:///feedback.db",
    invite_policy={"error": True, "p95_ms": 5000, "large_output_kb": 256},
    sample_neutral=0.10,
    ttl_hours=24
)

# Your server now collects feedback transparently
```

### Using Opt-out Controls

```python
# Opt out specific functions
@survey.opt_out(reason="contains sensitive data")
def run_sensitive_query(sql: str) -> dict:
    return execute_query(sql)

# Suppress collection for a block of code
with survey.suppressed(reason="benchmark"):
    for _ in range(1000):
        call_some_tool()
```

### Running a Server

```python
from skald.transport import TCPTransport

# Create transport and serve
transport = TCPTransport(survey)
await transport.serve(host="0.0.0.0", port=8765)
```

## CLI Usage

Skald includes a CLI for running demo servers and querying feedback data:

```bash
# Run over TCP
skald tcp --host localhost --port 8765

# Run over stdio  
skald stdio

# Query stored feedback
skald query --store sqlite:///feedback.db --limit 10

# Clean up expired data
skald cleanup --store sqlite:///feedback.db --ttl-hours 24
```

## Agent Integration

To collect feedback from AI agents, add this line to your system prompt:

```
When a tool provides a trace_id in its response metadata and invite_feedback=true, you may optionally use feedback.report to provide structured feedback on the tool's helpfulness (1-5), fit (1-5), clarity (1-5), confidence (0.0-1.0), and up to 3 short suggestions for improvement.
```

## Feedback Schema

The `feedback.report` tool accepts this JSON schema:

```json
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "helpfulness": 4,
  "fit": 3, 
  "clarity": 5,
  "confidence": 0.8,
  "better_alternative": "different_tool",
  "suggestions": ["Try tool X", "Use parameter Y"],
  "notes": "This worked well overall"
}
```

### Fields

- `trace_id` (required): UUID from the tool response metadata
- `helpfulness` (required): How helpful was the tool (1-5)
- `fit` (required): How well did the tool fit the task (1-5)  
- `clarity` (required): How clear was the tool output (1-5)
- `confidence` (required): Confidence in this feedback (0.0-1.0)
- `better_alternative` (optional): Enum suggesting better alternatives
- `suggestions` (optional): Up to 3 suggestions, each ≤100 characters
- `notes` (optional): Additional notes

## Configuration

### Invite Policy

Control when feedback is invited:

```python
invite_policy = {
    "error": True,           # Invite on errors
    "timeout": True,         # Invite on timeouts  
    "p95_ms": 5000.0,       # Latency threshold (ms)
    "large_output_kb": 256.0 # Output size threshold (KB)
}
```

### Storage Configuration

```python
# SQLite (default)
store = "sqlite:///path/to/feedback.db"

# Custom storage backend
from skald.storage.sqlite import SQLiteStorage
storage = SQLiteStorage("/custom/path.db")
survey = SurveyingProxy(upstream, store=storage)
```

### Data Redaction

Configure custom data redaction:

```python
def custom_redactor(args: dict) -> dict:
    """Remove sensitive data from tool arguments."""
    redacted = args.copy()
    if 'password' in redacted:
        redacted['password'] = '[REDACTED]'
    return redacted

survey = SurveyingProxy(
    upstream=upstream,
    redactor=custom_redactor
)
```

## Storage Schema

Skald uses two main tables:

### tool_runs
- `trace_id` (PK): UUID trace identifier
- `timestamp`: Execution timestamp
- `agent_id`: ID of the calling agent
- `tool_name`: Name of the tool called
- `status`: success/error/timeout
- `latency_ms`: Execution latency in milliseconds
- `output_bytes`: Size of output in bytes
- `invite_feedback`: Whether feedback was invited
- `opt_out`: Whether collection was opted out
- `args_redacted`: Redacted tool arguments (JSON)

### tool_feedback
- `trace_id` (FK): Reference to tool_runs
- `agent_id`: ID of the agent providing feedback
- `helpfulness`: Helpfulness rating (1-5)
- `fit`: Fit rating (1-5)
- `clarity`: Clarity rating (1-5)
- `confidence`: Confidence score (0.0-1.0)
- `better_alternative`: Better alternative suggestion
- `suggestions`: List of suggestions (JSON)
- `notes`: Additional notes
- `valid`: Whether feedback passed validation
- `raw_json`: Raw feedback JSON
- `timestamp`: Feedback timestamp

## Architecture

Skald follows a clean architecture with these components:

- **Core**: `SurveyingProxy` - Main proxy class that wraps MCP servers
- **Schema**: Pydantic models for data validation
- **Storage**: Pluggable storage backends (SQLite default)
- **Transport**: Communication protocols (stdio, TCP, Unix sockets)
- **Decorators**: Opt-out mechanisms (`@opt_out`, `with suppressed()`)

## Development

### Setup

```bash
git clone https://github.com/sibyllinesoft/skald.git
cd skald
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,test]"
```

### Testing

```bash
pytest
pytest --cov=skald --cov-report=html
```

### Code Quality

```bash
black skald tests
isort skald tests  
mypy skald
ruff skald tests
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.