# D&D Image Generator

Generate fantasy artwork for D&D entities using AI image generation (DALL-E 3 or Stability.ai) with category-aware prompts.

**Status:** ✅ Complete - 4,508 images generated across 18 entity types

## Features

- 🎨 Category-aware prompts (spell schools, item types)
- 🤖 Multi-provider support (DALL-E 3, Stability.ai)
- 📦 Batch generation with resumable state
- 🔧 MCP integration for Claude Code
- 💾 Source-prefixed filenames (`output/{entityType}/stability-ai/{source}--{slug}.png`)
- 🔄 Retry logic and rate limiting
- 📊 Manifest tracking of generated images
- 🖼️ Multiple size conversions in WebP format (512px, 256px, 128px) - 90% smaller than PNG

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
│   └── stability-ai/
│       ├── phb--fireball.png
│       └── phb--magic-missile.png
├── items/
│   └── stability-ai/
│       ├── phb--longsword.png
│       └── dmg--potion-of-healing.png
├── conversions/
│   ├── 128/
│   │   └── spells/stability-ai/*.webp
│   ├── 256/
│   │   └── spells/stability-ai/*.webp
│   └── 512/
│       └── spells/stability-ai/*.webp
└── .manifest.json  # Tracks generation status
```

**Filename Convention**: Files use source-prefixed naming to match API slugs:
- API slug `phb:fireball` → Filename `phb--fireball.png`
- API slug `xge:absorb-elements` → Filename `xge--absorb-elements.png`
- Colons converted to `--` for macOS compatibility

**Note**: Original images are stored as PNG (1024x1024). Conversions are WebP for ~90% file size savings.

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

**Complete Collection: 4,508 images across 18 entity types**

| Entity Type | Images | Status |
|-------------|--------|--------|
| spells | 488 | ✅ 100% |
| items | 2,508 | ✅ 100% |
| monsters | 848 | ✅ 100% |
| classes | 133 | ✅ 100% |
| races | 117 | ✅ 100% |
| feats | 159 | ✅ 100% |
| proficiency_types | 85 | ✅ 100% |
| backgrounds | 36 | ✅ 100% |
| languages | 30 | ✅ 100% |
| skills | 18 | ✅ 100% |
| item_types | 16 | ✅ 100% |
| conditions | 15 | ✅ 100% |
| damage_types | 13 | ✅ 100% |
| item_properties | 11 | ✅ 100% |
| sources | 11 | ✅ 100% |
| spell_schools | 8 | ✅ 100% |
| sizes | 6 | ✅ 100% |
| ability_scores | 6 | ✅ 100% |

### WebP Conversion Stats

| Size | PNG | WebP | Savings |
|------|-----|------|---------|
| 128px | 123 MB | 18.5 MB | 85% |
| 256px | 420 MB | 51.4 MB | 88% |
| 512px | 1.4 GB | 134.5 MB | 91% |
| **Total** | **2.0 GB** | **204 MB** | **90%** |

## API Routing

The D&D API uses different URL prefixes for different entity types:

- **Main entities** (spells, items, classes, races, backgrounds, monsters, feats) → `/api/v1/{entity}`
- **Lookup entities** (sources, spell-schools, damage-types, sizes, ability-scores, skills, item-types, item-properties, conditions, proficiency-types, languages) → `/api/v1/lookups/{entity}`

The image generator handles this routing automatically.

## Cost Estimation

**Provider Pricing (as of 2024):**
- **DALL-E 3:** Standard quality 1024x1024: ~$0.04/image
- **Stability.ai:** Stable Diffusion XL: ~$0.01/image

**Total Project Cost (using Stability.ai):** ~$45.08 for 4,508 images

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
