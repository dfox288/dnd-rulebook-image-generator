# D&D Image Generator Design

**Date:** 2025-11-22
**Status:** Design Complete

## Overview

A hybrid CLI/MCP image generation system that consumes the D&D Compendium API and generates fantasy-style artwork using OpenAI's DALL-E 3. Images are saved with predictable naming (`{entityType}/{slug}.png`) for easy frontend integration.

## Architecture

### Components

1. **Core Generator Module** (`src/generator/`)
   - `api_client.py` - Fetch data from D&D Compendium API
   - `prompt_builder.py` - Extract flavor text, build category-aware DALL-E prompts
   - `image_generator.py` - Call DALL-E API with retry logic
   - `file_manager.py` - Save images to `output/{entity_type}/{slug}.png`

2. **CLI Script** (`src/cli.py`)
   - Batch generation with entity type filters
   - Progress tracking and resumable runs
   - Dry-run mode for cost estimation

3. **MCP Server** (`src/mcp_server.py`)
   - Exposes generation commands to Claude Code
   - Commands:
     - `generate_image(entity_type, slug, custom_prompt?)` - Single image generation
     - `batch_generate(entity_type, filters?)` - Batch generation
     - `list_generated()` - Show generated images

4. **Configuration** (`config.yaml`)
   - API endpoints and credentials
   - Entity-specific prompt templates with category support
   - DALL-E settings and cost controls

### File Structure

```
image-generator/
├── output/
│   ├── spells/
│   │   ├── fireball.png
│   │   └── magic-missile.png
│   ├── races/
│   ├── classes/
│   ├── items/
│   ├── backgrounds/
│   └── .manifest.json         # Track generated images
├── src/
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── prompt_builder.py
│   │   ├── image_generator.py
│   │   └── file_manager.py
│   ├── cli.py
│   └── mcp_server.py
├── config.yaml
├── requirements.txt
└── README.md
```

## Data Flow

### Batch Generation
```
CLI invoked with entity type filter
  ↓
Fetch entities from D&D API (paginated)
  ↓
For each entity:
  ├─ Extract flavor text from description/traits
  ├─ Extract category (item_type, spell school, etc.)
  ├─ Build entity-specific prompt with category
  ├─ Call DALL-E API (with retry/backoff)
  ├─ Save to output/{entity_type}/{slug}.png
  └─ Update .manifest.json
  ↓
Generate summary report (successes/failures/costs)
```

### MCP Generation
```
Claude Code issues MCP command
  ↓
MCP server validates parameters
  ↓
Delegates to generator module (same flow as batch)
  ↓
Returns status/path to Claude Code
```

## Prompt System

### Category-Aware Prompts

Prompts use entity type AND category information for context-aware generation:

**Template Variables:**
- `{flavor_text}` - Extracted description from API
- `{name}` - Entity name
- `{entity_type}` - spell/class/race/item/background
- `{category}` - Extracted category (item_type.name, school.name, etc.)
- `{custom}` - Optional custom text (MCP manual generation)

### Entity-Specific Configuration

**Spells:**
- Category: `school.name` (Evocation, Necromancy, etc.)
- Prompt: `"D&D {category} spell effect: {flavor_text}. Magical energy, spell casting scene."`
- Source: `description` field

**Items:**
- Category: `item_type.name` (Weapon, Wondrous Item, Armor, etc.)
- Prompt: `"D&D {category} item: {flavor_text}. Product illustration, detailed object art."`
- Source: `description` field

**Classes:**
- Category: None
- Prompt: `"D&D character class portrait: {flavor_text}. Heroic pose, detailed equipment."`
- Source: `description` field (already rich)

**Races:**
- Category: `size.name` (optional)
- Prompt: `"Fantasy race character portrait: {flavor_text}. Cultural details, distinctive features."`
- Source: Trait descriptions (may need detail endpoints)

**Backgrounds:**
- Category: None
- Prompt: `"D&D background scene: {flavor_text}. Environmental storytelling, occupation details."`
- Source: Feature text (may need detail endpoints)

### Example Assembled Prompts

**Fireball (Evocation spell):**
```
D&D Evocation spell effect: A bright streak flashes from your pointing finger
to a point you choose within range and then blossoms with a low roar into an
explosion of flame. Magical energy, spell casting scene, visual effects.
```

**Absorbing Tattoo (Wondrous Item):**
```
D&D Wondrous Item item: Produced by a special needle, this magic tattoo features
designs that emphasize one color. Product illustration, detailed object art,
fantasy item.
```

## Technical Specifications

### DALL-E Configuration

- **Model:** `dall-e-3` (latest version)
- **Size:** `1024x1024` (standard size for DALL-E 3)
- **Quality:** `standard` (cost-effective, not `hd`)
- **Style:** `vivid` (dramatic/fantasy aesthetic)
- **Post-processing:** Optional resize to 512x512 for smaller frontend images
- **Cost:** ~$0.04/image (standard quality)

### API Integration

**D&D Compendium API:**
- Base URL: `http://localhost:8080/api/v1`
- Pagination support for bulk fetching
- Entity endpoints: `/spells`, `/items`, `/classes`, `/races`, `/backgrounds`

**OpenAI API:**
- Authentication via `OPENAI_API_KEY` environment variable
- Rate limiting: 2-second delay between requests
- Retry logic: Exponential backoff (3 retries max)

### Error Handling

**API Failures:**
- DALL-E rate limits → Exponential backoff with configurable max retries
- Content policy violations → Log entity, skip, continue batch
- Network errors → Retry with timeout

**State Management:**
- Track generated images in `output/.manifest.json`
- Skip already-generated images unless `--force-regenerate` flag
- Resume interrupted batch runs from checkpoint

**Cost Controls:**
- Dry-run mode to preview generation plan
- Entity limits per run (e.g., first 10 for testing)
- Pre-run cost estimation

### Configuration Schema

```yaml
api:
  base_url: "http://localhost:8080/api/v1"
  timeout: 30

openai:
  api_key: "${OPENAI_API_KEY}"
  model: "dall-e-3"
  size: "1024x1024"
  quality: "standard"
  style: "vivid"

output:
  base_path: "./output"
  post_resize: 512  # Optional: resize after generation

prompts:
  # Global defaults
  default:
    prefix: "Fantasy art in D&D style: "
    suffix: ". Digital art, dramatic lighting, detailed rendering."
    max_length: 1000
    include_category: false

  # Entity-specific overrides with category support
  spells:
    prefix: "D&D {category} spell effect: "
    suffix: ". Magical energy, spell casting scene, visual effects."
    include_category: true
    category_field: "school.name"
    style_keywords: ["magical", "energy", "glowing", "dynamic"]
    emphasis: "focus on the magical effect and visual impact"

  items:
    prefix: "D&D {category} item: "
    suffix: ". Product illustration, detailed object art, fantasy item."
    include_category: true
    category_field: "item_type.name"
    style_keywords: ["item illustration", "detailed object", "equipment"]
    emphasis: "focus on the physical object and its magical properties"

  classes:
    prefix: "D&D character class portrait: "
    suffix: ". Heroic pose, detailed armor and equipment, character concept art."
    include_category: false
    style_keywords: ["heroic", "character design", "detailed costume"]
    emphasis: "focus on the character archetype and iconic equipment"

  races:
    prefix: "Fantasy race character portrait: "
    suffix: ". Detailed facial features, cultural elements, character art."
    include_category: false
    style_keywords: ["portrait", "cultural details", "fantasy race"]
    emphasis: "focus on distinctive racial features and cultural aesthetics"

  backgrounds:
    prefix: "D&D background scene: "
    suffix: ". Environmental storytelling, occupation details, narrative scene."
    include_category: false
    style_keywords: ["environmental", "storytelling", "occupation"]
    emphasis: "focus on the profession or life story elements"

generation:
  max_retries: 3
  retry_delay: 5  # seconds
  batch_delay: 2  # seconds between images to avoid rate limits
```

## Flavor Text Extraction Strategy

Different entity types require different extraction logic:

- **Spells:** Primary `description` field + first sentence of `higher_levels` if available
- **Classes:** Full `description` field (already rich and visual)
- **Items:** `description` field + `detail` if present
- **Races:** Trait descriptions (may require detail endpoint call)
- **Backgrounds:** Feature text + personality traits (may require detail endpoint)

**Smart truncation:** Truncate at sentence boundaries to stay within DALL-E's prompt limits, not mid-word.

## CLI Usage Examples

```bash
# Batch generate all spells
python src/cli.py --entity-type spells

# Dry run to estimate costs
python src/cli.py --entity-type items --dry-run

# Generate first 10 items for testing
python src/cli.py --entity-type items --limit 10

# Force regenerate existing images
python src/cli.py --entity-type spells --force-regenerate

# Generate specific entity
python src/cli.py --entity-type spells --slug fireball
```

## MCP Integration

The MCP server enables manual control through Claude Code:

```python
# Generate single image
generate_image(entity_type="spells", slug="fireball")

# Generate with custom prompt override
generate_image(
    entity_type="items",
    slug="longsword",
    custom_prompt="ancient elven longsword with glowing runes"
)

# Batch generate filtered set
batch_generate(entity_type="items", filters={"item_type_id": 2})

# List what's been generated
list_generated()
```

## Success Criteria

- ✅ Images organized as `output/{entityType}/{slug}.png` for predictable frontend access
- ✅ Category-aware prompts that distinguish between item types, spell schools, etc.
- ✅ Resumable batch generation with cost controls
- ✅ MCP integration for manual generation via Claude Code
- ✅ Smaller image sizes (512x512 or 1024x1024) suitable for UI thumbnails
- ✅ Error handling for API failures and content policy violations

## Future Enhancements

- Support for additional entity types (feats, monsters, etc.)
- Image variation generation (multiple styles per entity)
- Upscaling/downscaling options
- Cache warming strategy for frequently accessed entities
- Integration with CDN for frontend serving
