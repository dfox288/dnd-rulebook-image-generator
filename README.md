# D&D Image Generator

Generate fantasy artwork for D&D entities using AI image generation (DALL-E 3 or Stability.ai) with category-aware prompts.

**Status:** ✅ Complete - 3,803 images generated across 11 entity types

## Features

- 🎨 Category-aware prompts (spell schools, item types)
- 🤖 Multi-provider support (DALL-E 3, Stability.ai)
- 📦 Batch generation with resumable state
- 🔧 MCP integration for Claude Code
- 💾 Organized output structure (`output/{entityType}/{slug}.png`)
- 🔄 Retry logic and rate limiting
- 📊 Manifest tracking of generated images
- 🖼️ Multiple size conversions (1024x1024, 512x512, 256x256)

## Setup

### Prerequisites

- Python 3.11+
- API key for your chosen provider:
  - OpenAI API key (for DALL-E 3)
  - Stability.ai API key (for Stable Diffusion)

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

## Generated Image Compendium

**Complete Collection: 3,803 images**

| Entity Type | Images Generated | API Coverage |
|-------------|------------------|--------------|
| classes | 209 | ✅ 100% (131 in API) |
| races | 131 | ✅ 100% (67 in API) |
| spells | 477 | ✅ 100% |
| items | 2,156 | ✅ 100% |
| backgrounds | 34 | ✅ 100% |
| monsters | 598 | ✅ 100% |
| feats | 138 | ✅ 100% |
| languages | 30 | ✅ 100% |
| sizes | 6 | ✅ 100% |
| item_types | 16 | ✅ Complete |
| spell_schools | 8 | ✅ Complete |

## Cost Estimation

**Provider Pricing (as of 2024):**
- **DALL-E 3:** Standard quality 1024x1024: ~$0.04/image
- **Stability.ai:** Stable Diffusion XL: ~$0.01/image

**Total Project Cost (using Stability.ai):** ~$38.03 for 3,803 images

Example costs:
- 100 spells: ~$1.00 (Stability) or ~$4.00 (DALL-E)
- 500 items: ~$5.00 (Stability) or ~$20.00 (DALL-E)

Use `--dry-run` to preview before generating.

## Troubleshooting

**API Rate Limits:** Adjust `batch_delay` in `config.yaml` (default: 2 seconds)

**Content Policy Violations:** Some descriptions may be rejected. Check logs and manifest for failed entities.

**Missing Environment Variable:** Ensure `OPENAI_API_KEY` is set in `.env`

## License

MIT
