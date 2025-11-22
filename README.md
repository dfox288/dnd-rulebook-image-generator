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

## MCP Server Setup

Add to your Claude Code MCP settings:

```json
{
  "dnd-image-generator": {
    "command": "python",
    "args": ["/path/to/image-generator/src/mcp_server.py"]
  }
}
```

Available commands:
- `generate_image(entity_type, slug, custom_prompt?)` - Generate single image
- `batch_generate(entity_type, limit?)` - Batch generate images
- `list_generated(entity_type?)` - List generated images
