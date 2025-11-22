# D&D Image Generator

Generate fantasy artwork for D&D entities using DALL-E 3 with category-aware prompts.

## Features

- 🎨 Category-aware prompts (spell schools, item types)
- 📦 Batch generation with resumable state
- 🔧 MCP integration for Claude Code
- 💾 Organized output structure (`output/{entityType}/{slug}.png`)
- 🔄 Retry logic and rate limiting
- 📊 Manifest tracking of generated images

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### CLI Batch Generation

```bash
# Generate first 10 spells
python src/cli.py --entity-type spells --limit 10

# Dry run to preview (no API calls)
python src/cli.py --entity-type items --dry-run

# Generate specific entity
python src/cli.py --entity-type spells --slug fireball

# Force regenerate existing images
python src/cli.py --entity-type classes --force-regenerate
```

### MCP Server for Claude Code

Add to your Claude Code MCP settings (`.claude/settings.json` or `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "dnd-image-generator": {
      "command": "python",
      "args": ["/absolute/path/to/image-generator/src/mcp_server.py"]
    }
  }
}
```

Available MCP commands in Claude Code:
- `generate_image(entity_type="spells", slug="fireball")` - Generate single image
- `generate_image(entity_type="items", slug="longsword", custom_prompt="ancient elven blade")` - Custom prompt
- `batch_generate(entity_type="items", limit=10)` - Batch generate
- `list_generated(entity_type="spells")` - List generated images

## Configuration

Edit `config.yaml` to customize:

- **Prompt templates** - Adjust prefix/suffix for each entity type
- **DALL-E settings** - Model, size, quality, style
- **Output settings** - Base path, post-resize dimensions
- **Rate limiting** - Retry delays, batch delays

Example entity-specific prompts:

```yaml
prompts:
  spells:
    prefix: "D&D {category} spell effect: "  # {category} = school name
    suffix: ". Magical energy, spell casting scene."
    include_category: true
    category_field: "school.name"
```

## Output Structure

```
output/
├── spells/
│   ├── fireball.png
│   └── magic-missile.png
├── items/
│   ├── longsword.png
│   └── potion-of-healing.png
├── classes/
├── races/
├── backgrounds/
└── .manifest.json  # Tracks generation status
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_config.py -v

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## Cost Estimation

DALL-E 3 pricing (as of 2024):
- Standard quality 1024x1024: ~$0.04/image

Example costs:
- 100 spells: ~$4.00
- 500 items: ~$20.00

Use `--dry-run` to preview before generating.

## Troubleshooting

**API Rate Limits:** Adjust `batch_delay` in `config.yaml` (default: 2 seconds)

**Content Policy Violations:** Some descriptions may be rejected. Check logs and manifest for failed entities.

**Missing Environment Variable:** Ensure `OPENAI_API_KEY` is set in `.env`

## License

MIT
