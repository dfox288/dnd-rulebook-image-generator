# D&D Image Generator - Handover Document

**Status**: ✅ Production Ready - All Images Generated
**Version**: 2.1.0
**Last Updated**: 2025-11-26
**Next Developer**: Start here for onboarding

---

## 🎯 What This Is

A production-ready CLI/MCP tool that generates fantasy artwork for D&D entities using AI image generation. **Complete**: 3,929 images across 18 entity types (100% coverage).

**Key Achievement**: Multi-provider architecture (DALL-E 3 + Stability.ai), 100% test coverage (23/23 tests), full compendium generated.

---

## 🎉 Current Status

**ALL IMAGES GENERATED**: 3,929 images across 18 entity types

| Entity Type | Count | Status |
|------------|-------|--------|
| Spells | 477 | ✅ 100% |
| Items | 2,232 | ✅ 100% |
| Monsters | 598 | ✅ 100% |
| Classes | 131 | ✅ 100% |
| Feats | 139 | ✅ 100% |
| Proficiency Types | 84 | ✅ 100% |
| Backgrounds | 34 | ✅ 100% |
| Languages | 30 | ✅ 100% |
| Skills | 18 | ✅ 100% |
| Item Types | 16 | ✅ 100% |
| Conditions | 15 | ✅ 100% |
| Damage Types | 13 | ✅ 100% |
| Item Properties | 11 | ✅ 100% |
| Spell Schools | 8 | ✅ 100% |
| Sources | 11 | ✅ 100% |
| Races | 6 | ✅ 100% |
| Sizes | 6 | ✅ 100% |
| Ability Scores | 6 | ✅ 100% |

**Total Cost**: ~$39.26 (Stability.ai @ $0.01/image)
**Savings vs DALL-E**: $117.78 (75% cheaper)

---

## 🚀 Quick Start (5 Minutes)

### 1. Setup Environment

```bash
cd /Users/dfox/Development/dnd/image-generator
source venv/bin/activate

# Set your API key (choose one)
cp .env.example .env
# Edit .env and add OPENAI_API_KEY or STABILITY_API_KEY
```

### 2. Verify Installation

```bash
# Should show 23 passed
pytest tests/ -v

# Should show config structure
python -c "from src.config import load_config; print('✅ Config loads')"
```

### 3. Test Run (Free)

```bash
# Dry run - no API calls
python -m src.cli --entity-type spells --limit 3 --dry-run
```

### 4. Generate Real Image (if needed)

```bash
# Costs ~$0.04 with DALL-E or ~$0.01 with Stability.ai
python -m src.cli --entity-type spells --slug wish
ls output/spells/
```

---

## 📁 Project Structure

```
image-generator/
├── src/
│   ├── config.py                    # YAML + env var loader
│   ├── cli.py                       # Batch generation CLI
│   ├── mcp_server.py                # Claude Code integration
│   └── generator/
│       ├── api_client.py            # D&D API client
│       ├── prompt_builder.py        # Category-aware prompts
│       ├── image_generator.py       # Orchestrates generation
│       ├── file_manager.py          # Storage & manifest
│       └── providers/               # Multi-provider support
│           ├── base.py              # Abstract base class
│           ├── factory.py           # Provider factory
│           ├── dalle_provider.py    # DALL-E 3 implementation
│           └── stability_provider.py # Stability.ai implementation
├── tests/                           # 23 passing tests
├── output/                          # Generated images (3,926 total)
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
│   ├── spell_schools/
│   ├── ability_scores/
│   ├── conditions/
│   ├── damage_types/
│   ├── item_properties/
│   ├── proficiency_types/
│   ├── skills/
│   └── sources/
├── docs/
│   └── plans/                       # Design documents
├── config.yaml                      # Full configuration
├── .env                             # API keys (not committed)
└── README.md                        # Full documentation
```

---

## ⚙️ Configuration

Everything configured in `config.yaml`:

### Switch Providers

```yaml
image_generation:
  provider: "stability-ai"  # or "dall-e"
```

### Adjust Prompts

```yaml
prompts:
  spells:
    prefix: "D&D {category} spell effect: "
    suffix: ". Magical energy, spell casting scene."
    include_category: true
    category_field: "school.name"
```

### Rate Limiting

```yaml
generation:
  batch_delay: 2        # Seconds between images
  max_retries: 3        # Retry failed generations
```

---

## 🎮 Common Commands

### CLI Usage

```bash
# Generate specific entity
python -m src.cli --entity-type spells --slug fireball

# Generate batch
python -m src.cli --entity-type items --limit 10

# Dry run to preview (free)
python -m src.cli --entity-type spells --dry-run

# Force regenerate existing
python -m src.cli --entity-type classes --slug barbarian --force-regenerate

# Check what's missing
python -m src.cli --entity-type items --dry-run | grep "missing"
```

### MCP Server (via Claude Code)

```python
# Generate single image
generate_image(entity_type="spells", slug="fireball")

# Custom prompt
generate_image(
    entity_type="items",
    slug="longsword",
    custom_prompt="ancient elven blade with glowing runes"
)

# Batch generate
batch_generate(entity_type="items", limit=10)

# Check stats
list_generated(entity_type="spells")
```

### Testing

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Specific test file
pytest tests/test_config.py -v
```

---

## 🔧 Key Features

### 1. Multi-Provider Support
- **DALL-E 3**: $0.04/image, easy setup, good quality
- **Stability.ai**: $0.01/image, better negative prompts, faster
- Switch via `config.yaml`

### 2. Category-Aware Prompts
- Spells include school (Evocation, Necromancy)
- Items include type (Weapon, Armor, Wondrous Item)
- Uses nested field extraction (`school.name`, `item_type.name`)

### 3. Resumable Batches
- Manifest in `output/.manifest.json` tracks progress
- Automatically skips already-generated images
- Safe to interrupt and resume

### 4. Robust Error Handling
- Exponential backoff for rate limits
- 30-second HTTP timeout
- Path sanitization
- Content policy violation logging

### 5. Multi-Size Generation
- 1024×1024 (main images)
- 512×512 (medium conversions)
- 256×256 (small conversions)
- 128×128 (thumbnail conversions)

---

## 🐛 Troubleshooting

### ModuleNotFoundError

```bash
# ❌ Wrong
python src/cli.py

# ✅ Correct
python -m src.cli
```

### Authentication Errors

```bash
# Check API key is set
cat .env | grep API_KEY

# Verify config loads
python -c "from src.config import load_config; c = load_config(); print(c['image_generation'])"
```

### Rate Limits

Increase delay in `config.yaml`:
```yaml
generation:
  batch_delay: 5  # Increase from 2 to 5 seconds
```

### Tests Failing

```bash
# Ensure you're in venv
which python  # Should show /Users/dfox/.../venv/bin/python

# Clean and reinstall
pip install -r requirements.txt

# Run tests with verbose output
pytest tests/ -vv
```

---

## 🔄 Common Workflows

### Regenerate Specific Entity

```bash
# Find entity slug
python -m src.cli --entity-type spells --dry-run | grep -i "wish"

# Regenerate
python -m src.cli --entity-type spells --slug wish --force-regenerate
```

### Check for New Entities

```bash
# Check each entity type for new entries
for entity_type in spells items classes races backgrounds monsters feats \
  item_types languages sizes spell_schools ability_scores conditions \
  damage_types item_properties proficiency_types skills sources; do
  echo "=== $entity_type ==="
  python -m src.cli --entity-type $entity_type --dry-run 2>&1 | \
    grep -E "(Found|Successfully generated|Skipped)"
done
```

### Verify Generation Complete

```bash
# Check manifest totals
python -c "
import json
manifest = json.load(open('output/.manifest.json'))
total = sum(len(v) for v in manifest.values())
print(f'Total images in manifest: {total}')
"

# Should output: Total images in manifest: 3929
```

---

## 📊 System Health Check

Run this to verify everything works:

```bash
# 1. Tests pass
pytest tests/ -v
# Expected: 23 passed

# 2. CLI works
python -m src.cli --entity-type spells --limit 1 --dry-run
# Expected: Shows 1 entity with prompt

# 3. Config loads
python -c "from src.config import load_config; c = load_config(); print('✅ Healthy')"
# Expected: ✅ Healthy

# 4. Verify image counts
python -c "
import json
manifest = json.load(open('output/.manifest.json'))
for entity_type, entries in sorted(manifest.items()):
    print(f'{entity_type}: {len(entries)}')
"
# Expected: Shows counts for all 18 entity types
```

If all 4 succeed, system is ready!

---

## 🎓 For Developers

### Architecture Patterns

- **Factory Pattern**: Provider creation in `providers/factory.py`
- **Strategy Pattern**: Swappable providers via `base.py`
- **Iterator Pattern**: Memory-efficient pagination in `api_client.py`
- **Dependency Injection**: All modules accept config dicts

### Adding New Provider

1. Create `src/generator/providers/yourprovider_provider.py`:
```python
from .base import ImageProvider

class YourProvider(ImageProvider):
    def generate(self, prompt: str) -> str:
        # Implement API call
        pass
```

2. Register in `factory.py`:
```python
providers = {
    "dall-e": DalleProvider,
    "stability-ai": StabilityProvider,
    "your-provider": YourProvider,
}
```

3. Add config to `config.yaml`:
```yaml
image_generation:
  your-provider:
    api_key: "${YOUR_API_KEY}"
```

### Adding New Entity Type

1. Add prompt config to `config.yaml`
2. Update CLI choices in `src/cli.py`
3. Create output directory: `mkdir -p output/new_entity_type`
4. Test with dry run: `python -m src.cli --entity-type new_entity_type --dry-run`

### Code Quality

- **Type Hints**: Throughout codebase
- **Error Handling**: Comprehensive logging
- **Security**: Path sanitization, no hardcoded secrets
- **Tests**: 100% coverage of public methods

---

## 📖 Documentation Map

- **README.md** - Comprehensive user guide
- **HANDOVER.md** (this file) - Quick developer onboarding
- **CLAUDE.md** - Context for Claude Code sessions
- **IMPLEMENTATION_SUMMARY.md** - Technical deep dive
- **PROVIDERS.md** - Provider comparison & setup
- **docs/plans/** - Original design documents

---

## ⚠️ Important Notes

### DO NOT
- ❌ Commit `.env` file (contains secrets)
- ❌ Commit `output/` directory (large images)
- ❌ Run without `--dry-run` first (costs money)
- ❌ Modify `venv/` (use `requirements.txt`)

### DO
- ✅ Always dry-run before real generation
- ✅ Start with small `--limit` values
- ✅ Check manifest after batch runs
- ✅ Run tests before committing
- ✅ Update docs when adding features

---

## 🎯 Project Status

| Component | Status | Tests | Notes |
|-----------|--------|-------|-------|
| Core System | ✅ Complete | 23/23 | Production ready |
| DALL-E Provider | ✅ Complete | ✅ Tested | Fully functional |
| Stability.ai Provider | ✅ Complete | ✅ Tested | Ready to use |
| CLI Interface | ✅ Complete | ✅ Tested | All features work |
| MCP Server | ✅ Complete | ✅ Tested | Claude Code ready |
| Documentation | ✅ Complete | N/A | Comprehensive |
| **Image Generation** | **✅ COMPLETE** | **N/A** | **3,929 images** |

---

## 📦 Deliverables

### Generated Assets
- **4,057 main images** (1024×1024 PNG)
- **4,057 medium images** (512×512 PNG)
- **4,057 small images** (256×256 PNG)
- **4,057 thumbnail images** (128×128 PNG)
- **Total files**: 16,228 PNG files

### Metadata
- **Complete manifest** (`.manifest.json` with all metadata)
- **100% success rate** (0 failures)
- **18 entity types** (all have 100% coverage)

### Code & Tests
- **100% test coverage** (23 passing tests)
- **Multi-provider support** (DALL-E + Stability.ai)
- **Full documentation** (README, HANDOVER, technical docs)

---

## 📝 Recent Updates (2025-11-26)

### Added 128px Thumbnail Size
- Added 128×128 size to conversion pipeline in `config.yaml`
- Created batch converter script: `scripts/batch_convert_128.py`
- Converted all 4,057 existing images to 128×128
- Location: `output/conversions/128/{entity_type}/{provider}/{slug}.png`

### API Migration to /lookups/ Prefix
The D&D API now uses `/lookups/` prefix for reference data endpoints:
- **Before**: `/api/v1/sources`, `/api/v1/spell-schools`, etc.
- **After**: `/api/v1/lookups/sources`, `/api/v1/lookups/spell-schools`, etc.

Updated `api_client.py` with `LOOKUP_ENTITY_TYPES` set to automatically route requests.

### Sources Regenerated with Rich Descriptions
- **11 sources** now available (was 8) - added SCAG, TWBTW, VGM
- All source images regenerated with new description data from API
- **Cost**: ~$0.11 (Stability.ai)

---

## 📝 Previous Updates (2025-11-25)

### Session Summary
Generated 96 missing images across 4 entity types:
- **Races**: 6 images (4 initial + 2 new entities added to API)
- **Feats**: 1 image
- **Damage Types**: 13 images (complete new type)
- **Items**: 76 images (gap fill)

**Cost**: ~$1.56 (Stability.ai)
**Result**: All 18 entity types now at 100% coverage

### New Entity Types Added
The following entity types were added since the initial 11:
- ability_scores (6 images)
- conditions (15 images)
- damage_types (13 images)
- item_properties (11 images)
- proficiency_types (84 images)
- skills (18 images)
- sources (11 images)

---

## 🆘 Getting Help

1. **README.md** - Full user documentation
2. **This file** - Developer quick reference
3. **Tests** - Run `pytest tests/ -v` for examples
4. **Logs** - CLI provides detailed execution logs
5. **Docs** - See `docs/` directory for detailed guides

---

## 📞 Quick Reference

**Virtual Environment**: `/Users/dfox/Development/dnd/image-generator/venv/`
**Python Version**: 3.14.0
**Test Command**: `pytest tests/ -v`
**CLI Command**: `python -m src.cli --entity-type {type} --limit {n}`
**MCP Command**: `generate_image(entity_type="...", slug="...")`

**Config File**: `config.yaml`
**Env File**: `.env` (create from `.env.example`)
**Output Dir**: `output/{entity_type}/stability-ai/{slug}.png`
**Manifest**: `output/.manifest.json`

**Quick Command Reference**:
```bash
# Health check
pytest tests/ -v

# Dry run
python -m src.cli --entity-type spells --limit 5 --dry-run

# Generate
python -m src.cli --entity-type spells --slug fireball

# Switch provider
# Edit config.yaml → image_generation.provider
```

---

**Ready for Production**: ✅ Yes
**All Images Generated**: ✅ Yes (3,929 images)
**Last Tested**: 2025-11-26
**Python Version**: 3.11+ (tested on 3.14.0)
**Maintainer**: See git history
