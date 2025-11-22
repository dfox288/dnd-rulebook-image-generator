# D&D API Entity Analysis - File Naming Convention

**Analysis Date**: 2025-11-22
**API Endpoint**: http://localhost:8080/docs/api.json

---

## Summary

The D&D API now provides **19 entity types** with varying slug support. This document outlines the file naming conventions for image generation.

---

## Entity Types by Slug Support

### ✅ Entities WITH `slug` Property (12 total)

These entities have proper slug fields that can be used directly for file naming:

| Entity Type | API Endpoint | Slug Field | Example | Config Status |
|------------|--------------|------------|---------|---------------|
| `spells` | `/v1/spells` | ✅ Yes | `fireball` | ✅ Configured |
| `items` | `/v1/items` | ✅ Yes | `longsword` | ✅ Configured |
| `classes` | `/v1/classes` | ✅ Yes | `wizard` | ✅ Configured |
| `races` | `/v1/races` | ✅ Yes | `elf` | ✅ Configured |
| `backgrounds` | `/v1/backgrounds` | ✅ Yes | `acolyte` | ✅ Configured |
| `monsters` | `/v1/monsters` | ✅ Yes | `adult-red-dragon` | ✅ Configured |
| `feats` | `/v1/feats` | ✅ Yes | `alert` | ✅ Configured |
| `languages` | `/v1/languages` | ✅ Yes | `common` | ✅ Configured |
| `conditions` | `/v1/conditions` | ✅ Yes | `blinded` | ✅ Configured |
| `proficiency-types` | `/v1/proficiency-types` | ✅ Yes | `armor` | ✅ Configured |
| `skills` | `/v1/skills` | ✅ Yes | `acrobatics` | ✅ Configured |

**File Naming**: Use `{slug}.png` directly
- Example: `output/spells/fireball.png`
- Example: `output/conditions/blinded.png`

---

### ⚠️ Entities WITHOUT `slug` Property (7 total)

These entities lack slug fields but have alternative identifiers:

| Entity Type | API Endpoint | Available Fields | Recommended Naming | Config Status |
|------------|--------------|------------------|-------------------|---------------|
| `item-types` | `/v1/item-types` | `id`, `code`, `name` | `{code}` (single letter) | ✅ Configured |
| `sizes` | `/v1/sizes` | `id`, `code`, `name` | `{code}` (single letter) | ✅ Configured |
| `spell-schools` | `/v1/spell-schools` | `id`, `code`, `name` | `{code}` (single letter) | ✅ Configured |
| `ability-scores` | `/v1/ability-scores` | `id`, `code`, `name` | `{code}` (3 letters: STR, DEX, etc.) | ✅ Configured |
| `damage-types` | `/v1/damage-types` | `id`, `name` | `slugify(name)` | ✅ Configured |
| `item-properties` | `/v1/item-properties` | `id`, `code`, `name` | `{code}` (single letter) | ✅ Configured |
| `sources` | `/v1/sources` | `id`, `code`, `name` | `{code}` (PHB, DMG, etc.) | ✅ Configured |

**Examples**:
- `output/spell-schools/A.png` (Abjuration)
- `output/sizes/T.png` (Tiny)
- `output/ability-scores/STR.png` (Strength)
- `output/damage-types/acid.png` (slugified from "Acid")
- `output/sources/PHB.png` (Player's Handbook)

---

## Recommended File Naming Strategy

### Primary Strategy (Preferred)
```python
# For entities WITH slug:
filename = f"{entity['slug']}.png"

# For entities WITHOUT slug but WITH code:
filename = f"{entity['code']}.png"

# For entities WITHOUT slug OR code:
filename = slugify(entity['name']) + ".png"
```

### Fallback Strategy (Universal)
```python
def get_filename(entity_data):
    """Get appropriate filename for any entity type."""
    if 'slug' in entity_data and entity_data['slug']:
        return f"{entity_data['slug']}.png"
    elif 'code' in entity_data and entity_data['code']:
        return f"{entity_data['code']}.png"
    else:
        # Slugify the name as last resort
        import re
        name = entity_data.get('name', 'unknown')
        slug = re.sub(r'[^\w\s-]', '', name).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)
        return f"{slug}.png"
```

---

## Sample Data Examples

### Entities with Slugs

**Spell** (`/v1/spells`):
```json
{
  "id": 383,
  "name": "Abi-Dalzim's Horrid Wilting",
  "slug": "abi-dalzims-horrid-wilting"
}
```
→ File: `abi-dalzims-horrid-wilting.png`

**Condition** (`/v1/conditions`):
```json
{
  "id": 1,
  "name": "Blinded",
  "slug": "blinded"
}
```
→ File: `blinded.png`

---

### Entities with Codes

**Spell School** (`/v1/spell-schools`):
```json
{
  "id": 1,
  "code": "A",
  "name": "Abjuration",
  "description": null
}
```
→ File: `A.png`

**Size** (`/v1/sizes`):
```json
{
  "id": 1,
  "code": "T",
  "name": "Tiny"
}
```
→ File: `T.png`

**Source** (`/v1/sources`):
```json
{
  "id": 1,
  "code": "PHB",
  "name": "Player's Handbook",
  "publisher": "Wizards of the Coast",
  "publication_year": 2014,
  "edition": "5e"
}
```
→ File: `PHB.png`

---

### Entities with Neither Slug nor Code

**Damage Type** (`/v1/damage-types`):
```json
{
  "id": 1,
  "name": "Acid"
}
```
→ File: `acid.png` (slugified from name)

---

## Implementation Recommendations

### 1. Update `file_manager.py`

Modify the filename generation logic to handle both slug-based and code-based naming:

```python
def _get_entity_filename(self, entity_data: Dict, entity_type: str) -> str:
    """Generate filename for entity based on available identifiers."""
    # Priority 1: Use slug if available
    if 'slug' in entity_data and entity_data['slug']:
        return f"{entity_data['slug']}.png"

    # Priority 2: Use code if available
    if 'code' in entity_data and entity_data['code']:
        return f"{entity_data['code']}.png"

    # Priority 3: Slugify name as fallback
    name = entity_data.get('name', 'unknown')
    slug = self._slugify_name(name)
    return f"{slug}.png"

def _slugify_name(self, name: str) -> str:
    """Convert name to URL-safe slug."""
    import re
    slug = re.sub(r'[^\w\s-]', '', name).strip().lower()
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug
```

### 2. Update Manifest Tracking

The manifest should track by the chosen identifier:

```json
{
  "spells": {
    "fireball": {"success": true, "timestamp": "2025-11-22T10:00:00Z"}
  },
  "spell_schools": {
    "A": {"success": true, "timestamp": "2025-11-22T10:00:00Z"},
    "E": {"success": true, "timestamp": "2025-11-22T10:00:00Z"}
  },
  "damage_types": {
    "acid": {"success": true, "timestamp": "2025-11-22T10:00:00Z"}
  }
}
```

### 3. CLI Argument Updates

For `--slug` CLI argument, treat it as a general identifier:

```bash
# Works for entities with slug
python -m src.cli --entity-type spells --slug fireball

# Works for entities with code
python -m src.cli --entity-type spell-schools --slug A

# Works for entities with name only
python -m src.cli --entity-type damage-types --slug acid
```

---

## Potential Naming Conflicts

### Single-Letter Codes

Entity types using single-letter codes (item-types, sizes, spell-schools, item-properties) are safe because:
- Limited character set (A-Z)
- Small entity counts (6-10 items each)
- No overlap within same entity type

**Example Counts**:
- Spell Schools: 8 schools (A-N range)
- Sizes: 6 sizes (T, S, M, L, H, G)
- Ability Scores: 6 scores (STR, DEX, CON, INT, WIS, CHA)

### Name-Based Slugification

For `damage-types` without codes, slugification is safe:
- Names are unique within entity type
- Standard slugification prevents special characters
- Examples: `acid`, `cold`, `fire`, `force`, `lightning`, `necrotic`, `poison`, `psychic`, `radiant`, `thunder`

---

## API Coverage Summary

| Category | Count | Status |
|----------|-------|--------|
| Total Entity Types | 19 | - |
| With Slug Support | 12 | ✅ Ready |
| With Code Fallback | 6 | ✅ Ready |
| Name-Only (Slugify) | 1 | ✅ Ready |
| **Configured in System** | **17** | **✅ Complete** |

---

## Next Steps

1. ✅ **Update `file_manager.py`** - Implement universal filename generation
2. ✅ **Update Tests** - Add test coverage for code-based and name-based naming
3. ✅ **Update CLI** - Accept identifier (slug/code/name) via `--slug` argument
4. ✅ **Update Documentation** - Reflect naming conventions in README
5. ⏳ **Validate** - Test generation for all entity types

---

## Configuration Status

All 17 entity types now have prompt configurations in `config.yaml`:

✅ spells, items, classes, races, backgrounds, monsters, feats, item_types, languages, sizes, spell_schools, ability_scores, conditions, damage_types, item_properties, proficiency_types, skills, sources

**Not Configured** (API exists but no prompt config):
- None! All entity types are configured.

---

**Conclusion**: The system is ready to handle all 19 entity types with appropriate fallback naming strategies. Slug-based naming is preferred, code-based is the fallback, and name slugification is the last resort.
