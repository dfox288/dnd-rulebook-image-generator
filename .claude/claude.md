# D&D Image Generator - Claude Code Context

**Project Type**: Python CLI/MCP Tool
**Status**: ✅ Complete - 4,508 images generated across 18 entity types
**Last Updated**: 2025-12-11

---

## Quick Context

This is a **complete, production-ready** image generation system that creates fantasy artwork for D&D entities using AI image generation (DALL-E 3 or Stability.ai). It features multi-provider support, category-aware prompts (spell schools, item types), resumable batch generation, and Claude Code integration via MCP server.

**Key Achievement**: Multi-provider architecture with hybrid CLI/MCP interface, automatic API routing for `/lookups/` endpoints, and comprehensive test coverage.

---

## Project Structure

```
/Users/dfox/Development/dnd/image-generator/
├── src/                          # Main source code
│   ├── config.py                 # Configuration loader (YAML + env vars)
│   ├── cli.py                    # Batch generation CLI
│   ├── mcp_server.py             # Claude Code MCP integration
│   └── generator/                # Core generation modules
│       ├── api_client.py         # D&D API client (pagination)
│       ├── prompt_builder.py     # Category-aware prompts
│       ├── image_generator.py    # Generation orchestrator
│       ├── file_manager.py       # Storage & manifest
│       └── providers/            # Multi-provider support
│           ├── base.py           # Abstract provider interface
│           ├── factory.py        # Provider factory
│           ├── dalle_provider.py # DALL-E 3 implementation
│           └── stability_provider.py # Stability.ai implementation
├── tests/                        # 23 passing tests
│   ├── test_config.py
│   ├── test_api_client.py
│   ├── test_prompt_builder.py
│   ├── test_image_generator.py
│   ├── test_file_manager.py
│   └── test_integration.py
├── output/                       # Generated images (gitignored)
│   ├── spells/
│   ├── items/
│   ├── classes/
│   ├── races/
│   ├── backgrounds/
│   ├── monsters/
│   ├── feats/
│   ├── item_types/
│   ├── languages/
│   ├── sizes/
│   └── spell_schools/
├── docs/plans/                   # Design & implementation docs
├── config.yaml                   # Full configuration
├── .env.example                  # Environment template
├── venv/                         # Virtual environment (Python 3.14)
└── README.md                     # Comprehensive docs
```

---

## 🎯 What This Does

1. **Fetches** D&D entities from API (auto-routes to correct endpoint)
   - Main entities: `http://localhost:8080/api/v1/{entity_type}`
   - Lookup entities: `http://localhost:8080/api/v1/lookups/{entity_type}`
2. **Extracts** flavor text from entity descriptions
3. **Builds** category-aware prompts (e.g., "D&D Evocation spell effect: fireball...")
4. **Generates** images via AI provider (DALL-E 3 @ $0.04 or Stability.ai @ $0.01 per image)
5. **Saves** to `output/{entityType}/stability-ai/{source}--{slug}.png`
   - Filenames use `--` separator (e.g., `phb--fireball.png`, `xge--absorb-elements.png`)
   - Colons from API slugs converted to `--` for macOS compatibility
6. **Tracks** state in `.manifest.json` for resumability

**Lookup Entity Types** (routed to `/lookups/`): sources, spell-schools, damage-types, sizes, ability-scores, skills, item-types, item-properties, conditions, proficiency-types, languages

---

## 🚀 Quick Commands

### Using the CLI

```bash
# Activate virtual environment first
source venv/bin/activate

# Dry run (free, no API calls)
python -m src.cli --entity-type spells --limit 5 --dry-run

# Generate real images (cost depends on provider)
# DALL-E: $0.04/image, Stability.ai: $0.01/image
python -m src.cli --entity-type spells --limit 5

# Generate specific entity
python -m src.cli --entity-type spells --slug fireball

# Run all tests
pytest tests/ -v  # Should show 23 passed
```

### Using MCP Server (via Claude Code)

```python
# Generate single image
generate_image(entity_type="spells", slug="fireball")

# Custom prompt override
generate_image(
    entity_type="items",
    slug="longsword",
    custom_prompt="ancient elven longsword with glowing runes"
)

# Batch generate
batch_generate(entity_type="items", limit=10)

# Check stats
list_generated(entity_type="spells")
```

---

## 🔑 Key Features

### 1. Multi-Provider Support
Supports multiple AI image generation providers:
- **DALL-E 3**: $0.04/image, reliable, good quality
- **Stability.ai**: $0.01/image, faster, better negative prompts
- Switch providers via `config.yaml` (`image_generation.provider`)
- Each provider optimized with specific configurations

### 2. Category-Aware Prompts
Automatically includes entity categories in prompts:
- **Spells**: School name (Evocation, Necromancy, etc.)
- **Items**: Item type (Weapon, Wondrous Item, Armor, etc.)
- Uses nested field extraction (`school.name`, `item_type.name`)

**Example**:
```
Entity: Fireball (Evocation spell)
Prompt: "D&D Evocation spell effect: A bright streak flashes from your
pointing finger to a point you choose within range and then blossoms
with a low roar into an explosion of flame. Magical energy, spell
casting scene, visual effects."
```

### 3. Resumable Batch Generation
- Manifest tracking in `output/.manifest.json`
- Automatically skips already-generated images
- Continues from where it left off if interrupted
- Tracks success/failure status

### 4. Robust Error Handling
- Exponential backoff for rate limits (3 retries)
- 30-second timeout on all HTTP requests
- Path sanitization prevents directory traversal
- Content policy violations logged and skipped

### 5. Dual Interface
- **CLI**: For automated batch generation
- **MCP Server**: For manual control via Claude Code

---

## 📋 Implementation Details

### Technology Stack
- **Python**: 3.11+ (tested on 3.14.0)
- **OpenAI SDK**: 2.8.1 (DALL-E 3)
- **MCP SDK**: 1.22.0 (Claude Code integration)
- **Testing**: pytest 9.0.1 (23 tests, 100% passing)

### Architecture Patterns
- **Factory Pattern**: Provider creation via `providers/factory.py`
- **Strategy Pattern**: Swappable providers implementing common interface
- **Dependency Injection**: All modules accept config dicts
- **Iterator Pattern**: Memory-efficient pagination
- **Builder Pattern**: Prompt construction

### Provider Configurations

**DALL-E 3**:
- Model: `dall-e-3`
- Size: `1024x1024` (resized to `512x512`)
- Quality: `standard` ($0.04/image)
- Style: `vivid` (dramatic/fantasy)

**Stability.ai**:
- Model: `stable-diffusion-xl-1024-v1-0`
- Size: `1024x1024`
- CFG Scale: 7 (prompt adherence)
- Steps: 30 (quality vs speed)
- Cost: ~$0.01/image
- Negative prompts: Prevents UI elements, grids, text

---

## 🧪 Testing

All 23 tests passing:

```bash
pytest tests/ -v

# Test breakdown:
# - 4 config tests (YAML loading, env vars)
# - 3 API client tests (pagination, limits)
# - 7 prompt builder tests (categories, truncation)
# - 3 image generator tests (success, retry, failures)
# - 5 file manager tests (storage, manifest, resize)
# - 1 integration test (end-to-end workflow)
```

---

## ⚙️ Configuration

All settings in `config.yaml`:

### Entity-Specific Prompts

```yaml
prompts:
  spells:
    prefix: "D&D {category} spell effect: "
    suffix: ". Magical energy, spell casting scene."
    include_category: true
    category_field: "school.name"

  items:
    prefix: "D&D {category} item: "
    suffix: ". Product illustration, detailed object art."
    include_category: true
    category_field: "item_type.name"
```

### Rate Limiting

```yaml
generation:
  max_retries: 3
  retry_delay: 5      # Base delay in seconds
  batch_delay: 2      # Delay between images
```

---

## 💡 Common Use Cases

### For Claude Code Users

**Use Case 1**: Generate image for specific spell
```python
generate_image(entity_type="spells", slug="wish")
```

**Use Case 2**: Custom artistic direction
```python
generate_image(
    entity_type="spells",
    slug="fireball",
    custom_prompt="fireball spell in anime art style, dramatic action pose"
)
```

**Use Case 3**: Check generation progress
```python
list_generated(entity_type="spells")
# Returns: "Generated 127 images for spells"
```

### For CLI Users

**Use Case 1**: Test with small batch
```bash
python -m src.cli --entity-type spells --limit 10
```

**Use Case 2**: Check what's already generated
```bash
# Check coverage for any entity type
python -m src.cli --entity-type items --dry-run

# All entity types now have 100% coverage!
```

**Use Case 3**: Regenerate failed images
```bash
# Check manifest for failures
cat output/.manifest.json | jq '.spells | to_entries[] | select(.value.success == false)'

# Regenerate specific entity
python -m src.cli --entity-type spells --slug failed-spell --force-regenerate
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
**Fix**: Use `python -m src.cli` instead of `python src/cli.py`

### "Authentication failed"
**Fix**: Set `OPENAI_API_KEY` in `.env` file

### Rate limit errors
**Fix**: Increase `batch_delay` in `config.yaml` (e.g., from 2 to 5 seconds)

### D&D API not responding
**Fix**: Ensure backend is running at `http://localhost:8080`

---

## 📊 Complete Image Compendium - Final Stats

**Total Images Generated: 4,508** (with source-prefixed filenames)

| Entity Type | Images Generated | API Coverage | Cost (Stability.ai) |
|-------------|------------------|--------------|---------------------|
| Spells | 488 | ✅ 100% | $4.88 |
| Items | 2,508 | ✅ 100% | $25.08 |
| Monsters | 848 | ✅ 100% | $8.48 |
| Classes | 133 | ✅ 100% | $1.33 |
| Races | 117 | ✅ 100% | $1.17 |
| Backgrounds | 36 | ✅ 100% | $0.36 |
| Feats | 159 | ✅ 100% | $1.59 |
| Languages | 30 | ✅ 100% | $0.30 |
| Sizes | 6 | ✅ 100% | $0.06 |
| Item Types | 16 | ✅ 100% | $0.16 |
| Spell Schools | 8 | ✅ 100% | $0.08 |
| Ability Scores | 6 | ✅ 100% | $0.06 |
| Conditions | 15 | ✅ 100% | $0.15 |
| Damage Types | 13 | ✅ 100% | $0.13 |
| Item Properties | 11 | ✅ 100% | $0.11 |
| Proficiency Types | 85 | ✅ 100% | $0.85 |
| Skills | 18 | ✅ 100% | $0.18 |
| Sources | 11 | ✅ 100% | $0.11 |
| **TOTAL** | **4,508** | **✅ 100%** | **~$45.08** |

**Note**: All images generated using Stability.ai at ~$0.01/image. DALL-E 3 would have cost ~$180.32 at $0.04/image.

### Filename Convention

All files now use source-prefixed naming to match API slugs:
- API slug: `phb:fireball` → Filename: `phb--fireball.png`
- API slug: `xge:absorb-elements` → Filename: `xge--absorb-elements.png`
- API slug: `core:common` → Filename: `core--common.png` (lookup entities)

Source prefixes indicate the rulebook: `phb` (Player's Handbook), `xge` (Xanathar's Guide), `tce` (Tasha's Cauldron), `ftod` (Fizban's Treasury), `dmg` (Dungeon Master's Guide), `vgm` (Volo's Guide), `core` (core rules), etc.

### WebP Conversions

All conversion sizes are now stored as WebP format for ~90% file size reduction:

| Size | PNG | WebP | Savings |
|------|-----|------|---------|
| 128px | 123.0 MB | 18.5 MB | **85.0%** |
| 256px | 420.5 MB | 51.4 MB | **87.8%** |
| 512px | 1.4 GB | 134.5 MB | **90.8%** |
| **TOTAL** | **2.0 GB** | **204.4 MB** | **89.8%** |

---

## 🔄 Typical Workflow

### First-Time Setup
1. Set `OPENAI_API_KEY` in `.env`
2. Dry run: `python -m src.cli --entity-type spells --limit 3 --dry-run`
3. Test generation: `python -m src.cli --entity-type spells --limit 3`
4. Verify: `ls output/spells/`

### Current Status (Complete)
All 18 entity types have been fully generated with 4,508 images:
- ✅ All API entities have corresponding images
- ✅ Source-prefixed filenames (e.g., `phb--fireball.png`)
- ✅ Original images stored as PNG (1024x1024)
- ✅ Multi-size WebP conversions (512px, 256px, 128px) - 90% smaller than PNG
- ✅ Manifest tracking complete
- ✅ Total cost: ~$45.08 using Stability.ai

To regenerate or add new entities:
1. Use `--force-regenerate` flag to recreate existing images
2. New entities added to the API will be automatically detected

---

## 📚 Documentation Files

- **README.md** - User-facing documentation with complete usage guide
- **HANDOVER.md** - Quick start guide for next developer
- **IMPLEMENTATION_SUMMARY.md** - Technical details, architecture, test results
- **PROVIDERS.md** - Provider comparison and configuration guide
- **docs/plans/2025-11-22-dnd-image-generator-design.md** - Original design document
- **docs/plans/2025-11-22-implementation-plan.md** - Detailed implementation plan

---

## 🛡️ Security & Best Practices

### Implemented Security
✅ Path sanitization (prevents directory traversal)
✅ Request timeouts (30 seconds)
✅ No hardcoded secrets (env vars only)
✅ .gitignore excludes .env and output/

### Development Best Practices
✅ TDD methodology (tests written first)
✅ 100% test coverage of public methods
✅ Type hints throughout
✅ Comprehensive error handling
✅ Logging at appropriate levels

---

## 🎓 For Developers

### Adding New Entity Type

**Note**: The system now supports 18 entity types (spells, items, classes, races, backgrounds, monsters, feats, item_types, languages, sizes, spell_schools, ability_scores, conditions, damage_types, item_properties, proficiency_types, skills, sources). To add more:

1. Add prompt config to `config.yaml`:
```yaml
prompts:
  new_entity_type:
    entity_prefix: "a D&D"
    include_category: false
    # Optional: custom template (otherwise uses default)
    template: |
      Custom template here...
```

2. Update CLI choices in `src/cli.py`:
```python
choices=['spells', 'items', ..., 'new_entity_type']
```

3. Create output directory:
```bash
mkdir -p output/new_entity_type
```

### Modifying Prompts

Edit `config.yaml` → `prompts` section. Each entity type can have:
- `prefix`: Text before flavor (can include `{category}` placeholder)
- `suffix`: Text after flavor
- `include_category`: Boolean
- `category_field`: Dot-notation path (e.g., `"school.name"`)

### Running Tests During Development

```bash
# Watch mode (if pytest-watch installed)
ptw tests/

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

---

## ✅ System Health Check

Quick verification that everything works:

```bash
# 1. Tests pass
pytest tests/ -v  # Should show: 23 passed

# 2. CLI works
python -m src.cli --entity-type spells --limit 1 --dry-run

# 3. Config loads
python -c "from src.config import load_config; print(list(load_config().keys()))"
```

If all 3 succeed, system is healthy!

---

## 🔮 Future Enhancements (Optional)

Potential improvements not currently implemented:
- [ ] Progress bar for CLI batch operations
- [ ] Specific OpenAI exception handling
- [ ] Manifest thread safety (file locking)
- [ ] Image format validation
- [ ] Database backend for manifest (vs JSON file)
- [ ] CDN integration for serving images
- [ ] Prometheus metrics

---

## 📞 Quick Reference

**Virtual Environment**: `/Users/dfox/Development/dnd/image-generator/venv/`
**Python Version**: 3.14.0
**Test Command**: `pytest tests/ -v`
**CLI Command**: `python -m src.cli --entity-type {type} --limit {n}`
**MCP Command**: `generate_image(entity_type="...", slug="...")`

**Config File**: `config.yaml`
**Env File**: `.env` (create from `.env.example`)
**Output Dir**: `output/{entity_type}/stability-ai/{source}--{slug}.png`
**Manifest**: `output/.manifest.json`

---

**Status**: ✅ Complete - Full compendium of 4,508 images generated across 18 entity types
**Last Updated**: 2025-12-11
**Maintainer**: See git log for contributors
