# Instructions for Next Agent / User

**Project**: D&D Image Generator
**Status**: ✅ COMPLETE & READY FOR USE
**Last Updated**: 2025-11-22

---

## 🎯 What This Project Does

This is a **production-ready** image generation system that:
1. Fetches D&D entities (spells, items, classes, etc.) from a local API at `http://localhost:8080`
2. Extracts flavor text from entity descriptions
3. Builds category-aware prompts (e.g., "D&D Evocation spell: fireball...")
4. Generates fantasy artwork using OpenAI's DALL-E 3
5. Saves images to organized directories (`output/{entityType}/{slug}.png`)
6. Tracks generation state in a manifest for resumability

---

## 🚀 Quick Start (First Time)

### 1. Environment Setup

```bash
# Navigate to project
cd /Users/dfox/Development/dnd/image-generator

# Activate virtual environment
source venv/bin/activate

# Set your OpenAI API key
cp .env.example .env
# Edit .env and add your actual OPENAI_API_KEY
```

### 2. Test Run (FREE - No API Calls)

```bash
# Dry run - shows what would be generated without calling DALL-E
python -m src.cli --entity-type spells --limit 5 --dry-run
```

**Expected Output**:
```
Found 5 entities

1. Abi-Dalzim's Horrid Wilting (abi-dalzims-horrid-wilting)
   Prompt: D&D Necromancy spell effect: You draw the moisture...
   [DRY RUN] Would generate image

2. Absorb Elements (absorb-elements)
   Prompt: D&D Abjuration spell effect: The spell captures...
   [DRY RUN] Would generate image
...

GENERATION SUMMARY
Total entities: 5
Successfully generated: 5
```

### 3. Generate Real Images (COSTS MONEY)

```bash
# Generate 3 test images (~$0.12)
python -m src.cli --entity-type spells --limit 3

# Check output
ls -la output/spells/
```

---

## 📋 Common Commands

### CLI Usage

```bash
# Generate specific entity
python -m src.cli --entity-type spells --slug fireball

# Generate 10 items
python -m src.cli --entity-type items --limit 10

# Force regenerate existing images
python -m src.cli --entity-type classes --force-regenerate

# Generate all spells (477 images, ~$19)
python -m src.cli --entity-type spells
```

### Testing

```bash
# Run all tests (should see 23 passed)
pytest tests/ -v

# Run specific test file
pytest tests/test_config.py -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html
```

### Development

```bash
# View test coverage in browser
open htmlcov/index.html

# Check code with ruff (if installed)
ruff check src/

# Format code with black (if installed)
black src/ tests/
```

---

## 🔧 Configuration Customization

All settings are in `config.yaml`. Key areas:

### Adjust Image Quality/Cost

```yaml
openai:
  size: "1024x1024"      # Options: 1024x1024 (standard)
  quality: "standard"    # Options: standard ($0.04) or hd ($0.08)
  style: "vivid"         # Options: vivid (dramatic) or natural
```

### Modify Prompts

```yaml
prompts:
  spells:
    prefix: "D&D {category} spell effect: "
    suffix: ". Magical energy, spell casting scene."
    include_category: true
    category_field: "school.name"
```

**Template Variables Available**:
- `{category}` - Extracted from category_field (e.g., "Evocation")
- `{name}` - Entity name
- `{entity_type}` - Type (spells, items, etc.)

### Adjust Rate Limiting

```yaml
generation:
  max_retries: 3        # Retry failed generations
  retry_delay: 5        # Seconds between retries
  batch_delay: 2        # Seconds between each image
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"

**Solution**: Run with `python -m src.cli` instead of `python src/cli.py`

**Why**: The project uses package-style imports. The `-m` flag adds the current directory to Python's path.

### "Authentication failed" or "Invalid API key"

**Check**:
1. Is `OPENAI_API_KEY` set in `.env`?
2. Is the API key valid and active?
3. Run: `cat .env | grep OPENAI_API_KEY` to verify it's set

### Rate limit errors

**Solution**: Increase delays in `config.yaml`:
```yaml
generation:
  batch_delay: 5  # Increase from 2 to 5 seconds
```

### Content policy violations

**Symptom**: Some entities fail with content policy errors

**Solution**: Check `output/.manifest.json` for failed entities. Some D&D descriptions may violate OpenAI's content policy. These are logged and skipped automatically.

### Backend API not running

**Symptom**: `Connection refused` errors when fetching entities

**Solution**: Ensure the D&D Compendium API is running at `http://localhost:8080`

---

## 🔌 MCP Server Setup (Optional)

For manual control via Claude Code:

### 1. Configure Claude Code

Add to `~/.claude/settings.json` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "dnd-image-generator": {
      "command": "python",
      "args": ["/Users/dfox/Development/dnd/image-generator/src/mcp_server.py"]
    }
  }
}
```

### 2. Restart Claude Code

### 3. Use MCP Commands

```python
# Generate single image
generate_image(entity_type="spells", slug="fireball")

# Custom prompt
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

## 💰 Cost Management

### Before Large Batches

```bash
# Always dry-run first to see what will be generated
python -m src.cli --entity-type items --dry-run

# Check entity count in summary
# Multiply by $0.04 to estimate cost
```

### Entity Counts & Costs

| Entity Type | Count | Est. Cost |
|------------|-------|-----------|
| Spells | 477 | $19.08 |
| Items | 2,156 | $86.24 |
| Races | 115 | $4.60 |
| Classes | ~13 | $0.52 |
| Backgrounds | 34 | $1.36 |
| **TOTAL** | **~2,795** | **~$111.80** |

### Resumability

If interrupted, the system automatically:
- ✅ Skips already-generated images
- ✅ Continues from where it left off
- ✅ Tracks success/failure in manifest

```bash
# This is safe - will only generate new images
python -m src.cli --entity-type spells
```

---

## 📂 Output Structure

Generated images are organized by entity type:

```
output/
├── spells/
│   ├── fireball.png
│   ├── magic-missile.png
│   └── ...
├── items/
│   ├── longsword.png
│   ├── potion-of-healing.png
│   └── ...
├── classes/
├── races/
├── backgrounds/
└── .manifest.json         # Tracks what's been generated
```

### Manifest Format

`.manifest.json` tracks generation state:

```json
{
  "spells": {
    "fireball": {
      "path": "output/spells/fireball.png",
      "success": true,
      "error": null
    },
    "failed-spell": {
      "path": "",
      "success": false,
      "error": "Content policy violation"
    }
  }
}
```

---

## 🔄 Common Workflows

### Workflow 1: Generate Test Batch

```bash
# 1. Dry run to preview
python -m src.cli --entity-type spells --limit 5 --dry-run

# 2. Generate for real
python -m src.cli --entity-type spells --limit 5

# 3. Check results
ls -la output/spells/
open output/spells/fireball.png

# 4. Check manifest for failures
cat output/.manifest.json | jq '.spells | to_entries[] | select(.value.success == false)'
```

### Workflow 2: Regenerate Failed Images

```bash
# 1. Identify failed entities in manifest
cat output/.manifest.json | jq '.spells | to_entries[] | select(.value.success == false)'

# 2. Regenerate specific entity
python -m src.cli --entity-type spells --slug failed-spell-slug --force-regenerate
```

### Workflow 3: Generate All Entities of Type

```bash
# 1. Dry run to check count
python -m src.cli --entity-type items --dry-run

# 2. Generate (this will take a while and cost money)
python -m src.cli --entity-type items

# 3. Monitor progress in terminal
# 4. Check final summary for failures
```

### Workflow 4: Custom Prompt for One Entity

Using MCP server in Claude Code:

```python
generate_image(
    entity_type="spells",
    slug="fireball",
    custom_prompt="a massive explosion of fire engulfing a medieval battlefield, dramatic sunset lighting, epic fantasy art"
)
```

---

## 📊 Monitoring & Logs

### View Real-time Logs

The CLI outputs detailed logs:

```
INFO - Fetching spells...
INFO - Found 477 entities
INFO - [1/477] Processing: Fireball (fireball)
INFO -   Prompt: D&D Evocation spell effect: A bright streak...
INFO -   ✓ Generated: output/spells/fireball.png
INFO - [2/477] Processing: Magic Missile (magic-missile)
```

### Check Manifest for Summary

```bash
# Count successful generations
cat output/.manifest.json | jq '[.[] | to_entries[] | select(.value.success == true)] | length'

# List failed generations
cat output/.manifest.json | jq -r '.[][] | select(.success == false) | .error' | sort | uniq -c
```

---

## 🛠️ Advanced Usage

### Modify Prompts Per Entity

Edit `config.yaml` to customize prompts for each entity type:

```yaml
prompts:
  items:
    prefix: "D&D {category} item: "
    suffix: ". Product photography, detailed, isolated on white background."
    include_category: true
    category_field: "item_type.name"
```

### Change Image Size

```yaml
output:
  post_resize: 256  # Resize to 256x256 after generation (saves storage)
```

### Add New Entity Type

1. Add prompt config to `config.yaml`:
```yaml
prompts:
  feats:
    prefix: "D&D feat illustration: "
    suffix: ". Character ability, action scene."
    include_category: false
```

2. Update CLI choices in `src/cli.py` (line ~30):
```python
choices=['spells', 'items', 'classes', 'races', 'backgrounds', 'feats']
```

---

## 🧪 Testing Changes

### Before Making Code Changes

```bash
# Ensure all tests pass
pytest tests/ -v

# Should see: 23 passed in ~0.7s
```

### After Making Changes

```bash
# Run tests again
pytest tests/ -v

# If tests fail, check the error messages
# Fix issues until all 23 tests pass
```

### Adding New Tests

Add to appropriate test file in `tests/`:
- API changes → `test_api_client.py`
- Config changes → `test_config.py`
- Prompt changes → `test_prompt_builder.py`

---

## 📖 Documentation

- **README.md** - User-facing documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **docs/plans/2025-11-22-dnd-image-generator-design.md** - Original design
- **docs/plans/2025-11-22-implementation-plan.md** - Implementation plan with all tasks
- **THIS FILE** - Quick reference for next agent/user

---

## ⚠️ Important Notes

### DO NOT

- ❌ Commit `.env` file (contains API key)
- ❌ Commit `output/` directory (large image files)
- ❌ Run without dry-run first (costs money)
- ❌ Generate all entities without checking cost estimate
- ❌ Modify virtual environment packages without updating `requirements.txt`

### DO

- ✅ Use dry-run mode for testing
- ✅ Start with small limits (--limit 5)
- ✅ Check manifest for failures after batches
- ✅ Keep `OPENAI_API_KEY` in `.env` file only
- ✅ Run tests before committing changes
- ✅ Update documentation when adding features

---

## 🆘 Getting Help

### Check These First

1. **README.md** - Comprehensive usage guide
2. **This file** - Quick troubleshooting
3. **Test output** - Run `pytest tests/ -v` to verify system health
4. **Logs** - CLI provides detailed logs during execution

### Common Questions

**Q: Can I use this without the D&D API?**
A: No, this requires a running instance of the D&D Compendium API at localhost:8080

**Q: Can I change the DALL-E model?**
A: Yes, edit `config.yaml` → `openai.model`, but dall-e-3 is recommended

**Q: How do I stop a running batch?**
A: Press Ctrl+C. The manifest saves progress, so you can resume later.

**Q: Can I run multiple batches in parallel?**
A: Not recommended - manifest updates may conflict. Run sequentially.

---

## 🎓 Understanding the Codebase

### Entry Points

- **CLI**: `src/cli.py` - Main command-line interface
- **MCP Server**: `src/mcp_server.py` - Claude Code integration
- **Tests**: `tests/` - All test files

### Core Modules

- `src/config.py` - Loads `config.yaml`, substitutes env vars
- `src/generator/api_client.py` - Fetches entities from D&D API
- `src/generator/prompt_builder.py` - Builds DALL-E prompts with categories
- `src/generator/image_generator.py` - Calls DALL-E API with retry logic
- `src/generator/file_manager.py` - Saves images, tracks manifest

### Data Flow

```
D&D API → api_client → prompt_builder → image_generator → file_manager → output/
                                  ↓
                            config.yaml (prompts, settings)
```

---

## ✅ System Health Check

Run this to verify everything works:

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Run all tests
pytest tests/ -v
# Should see: 23 passed

# 3. Dry run CLI
python -m src.cli --entity-type spells --limit 3 --dry-run
# Should see: 3 entities with prompts

# 4. Check config loads
python -c "from src.config import load_config; c = load_config(); print('Config loaded:', list(c.keys()))"
# Should see: Config loaded: ['api', 'openai', 'output', 'prompts', 'generation']
```

If all 4 steps succeed, the system is healthy and ready to use!

---

**Last Updated**: 2025-11-22
**Next Review**: When adding new features or entity types
**Maintainer**: See git history for contributors
