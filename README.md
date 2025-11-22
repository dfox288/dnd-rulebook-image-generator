# D&D Image Generator

Generate fantasy artwork for D&D entities using DALL-E 3.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Add your OpenAI API key to .env
```

## Usage

```bash
# Batch generate spells
python src/cli.py --entity-type spells --limit 10

# Dry run
python src/cli.py --entity-type items --dry-run
```

## MCP Integration

Run the MCP server for Claude Code integration:

```bash
python src/mcp_server.py
```
