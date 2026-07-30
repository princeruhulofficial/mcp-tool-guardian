# MCP Tool Guardian

**Production-ready MCP Server for AI Agent Reliability & Accountability**

> Protect your AI agents from bad tool outputs, schema mismatches, and potential tool poisoning. Built for entrepreneurs who want safer, more accountable AI systems.

## The Problem (Simple Explanation)

Imagine your AI helper is like a 10-year-old kid who asks friends for information. Sometimes the friends give wrong, incomplete, or even tricky answers. The kid then makes mistakes because of that bad information.

MCP Tool Guardian is like a smart teacher who checks every answer the friends give **before** the kid uses it. It makes sure the answer matches the expected shape, cleans dangerous parts, and gives a reliability score.

This is especially useful for founders building AI products who care about trust and accountability (like Prevalid's mission).

## What This MCP Server Does

It exposes tools that any MCP-compatible AI agent (Claude Desktop, Cursor, Windsurf, etc.) can call:

| Tool | What it does (kid-friendly) |
|------|-----------------------------|
| `validate_against_schema` | Checks if the data looks exactly like the promised shape (like checking if a LEGO set has all the right pieces) |
| `sanitize_tool_output` | Cleans the data – removes secrets, weird characters, or possible injection tricks |
| `score_reliability` | Gives a score from 0-100 how trustworthy the tool answer is |
| `detect_suspicious_patterns` | Looks for common "poison" patterns that bad tools sometimes hide |
| `create_audit_entry` | Writes a simple log so you can later see what happened (accountability!) |

## Why This is Valuable for Entrepreneurs

- **Reduce AI failures**: Fewer cascading errors from bad tool data
- **Low cost**: Pure local computation – no expensive external APIs needed
- **Accountability**: Perfect for Prevalid-style AI Execution OS
- **Ready for production**: Stateless design compatible with new MCP 2026-07-28 spec
- **Easy to sell**: Can be packaged as a paid MCP or internal reliability layer

## Quick Start

### Requirements
- Python 3.10+
- `mcp` package (official SDK)

```bash
pip install mcp jsonschema pydantic
```

### Run the server

```bash
python -m src.server
```

Or with uv:
```bash
uv run python -m src.server
```

### Add to Claude Desktop / Cursor

Add this to your MCP config:

```json
{
  "mcpServers": {
    "tool-guardian": {
      "command": "python",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/mcp-tool-guardian-20260730"
    }
  }
}
```

## Project Structure

```
mcp-tool-guardian-20260730/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main MCP server
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── validate.py
│   │   ├── sanitize.py
│   │   ├── reliability.py
│   │   └── audit.py
│   └── utils/
│       └── schemas.py
├── tests/
│   └── test_tools.py
├── mcpize.yaml
├── .env.example
├── pyproject.toml
├── LAUNCH.md
└── README.md
```

## License

MIT – Build freely, stay accountable.

---

**Daily AI MCP Project by Grok for Prince Ruhul / Prevalid**  
Date: 2026-07-30
