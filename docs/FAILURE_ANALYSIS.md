# Generation Failure Analysis

**Date**: 2025-11-22
**Status**: API Currently Down (502 Bad Gateway)

---

## Summary

Found 2 failed generations out of 650 total entities (99.7% success rate):

1. **classes/artificer-artillerist** - JSON parsing error
2. **sizes/null** - NoneType slug error

---

## Failure Details

### 1. Class Failure: `artificer-artillerist`

**Entity Type**: `classes`
**Slug**: `artificer-artillerist`
**Error**: `Expecting value: line 1 column 1 (char 0)`

**Root Cause Analysis**:
- This is a JSON parsing error from the API response
- Likely causes:
  - API returned empty response (HTTP 204 or empty body)
  - API returned non-JSON content (HTML error page)
  - Network timeout/interruption during response

**Impact**:
- File path is empty (image was not saved)
- This is a valid entity that should exist

**Recommended Fix**:
```bash
# Once API is back online:
python -m src.cli --entity-type classes --slug artificer-artillerist
```

---

### 2. Size Failure: `null`

**Entity Type**: `sizes`
**Slug**: `null` (literal string "null")
**Error**: `argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'`

**Root Cause Analysis**:
- The API returned an entity with `slug: null` or missing slug field
- `file_manager.py:71` tries to sanitize the slug: `Path(slug).name`
- When slug is `None` (not a string), `Path()` raises TypeError

**Code Reference**: `src/generator/file_manager.py:71`
```python
# Current code (vulnerable to None):
sanitized_slug = Path(slug).name
```

**Impact**:
- File path is empty (image was not saved)
- This entity was skipped during generation

**Root Problem**:
The code assumes `slug` is always a string, but the API can return entities without slugs. For `sizes`, we should fall back to using the `code` field.

**Recommended Fix Options**:

**Option A: Update file_manager.py** (Proper fix)
```python
def save_image(self, image_url: str, entity_type: str, slug: str, ...):
    # Handle None/null slugs
    if slug is None or slug == "null":
        raise ValueError(f"Invalid slug for {entity_type}: {slug}")

    sanitized_slug = Path(slug).name
    # ... rest of code
```

**Option B: Update image_generator.py** (Preventive fix)
```python
# Before calling file_manager.save_image():
identifier = entity.get('slug') or entity.get('code') or slugify(entity.get('name'))
if not identifier:
    logger.error(f"Entity missing identifier: {entity}")
    continue
```

**Option C: Investigate specific entity**
```bash
# Once API is back:
curl "http://localhost:8080/api/v1/sizes" | jq '.data[] | select(.slug == null or .code == null)'
```

---

## Current Stats

| Entity Type | Total | Successful | Failed | Success Rate |
|------------|-------|------------|--------|--------------|
| classes | 131 | 130 | 1 | 99.2% |
| sizes | 7 | 6 | 1 | 85.7% |
| **Overall** | **650** | **648** | **2** | **99.7%** |

---

## API Status

**Current Status**: ❌ DOWN (502 Bad Gateway)
```
$ curl http://localhost:8080/api/v1/spells?per_page=1
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.29.3</center>
</body>
</html>
```

**Next Steps**:
1. ⏳ Wait for API to come back online
2. 🔍 Investigate the `sizes/null` entity via API
3. 🛠️ Decide if code changes are needed (add null-safety)
4. ♻️ Regenerate both failed entities
5. ✅ Verify 100% success rate

---

## Prevention Recommendations

### 1. Add Null-Safety to File Manager

Update `src/generator/file_manager.py:save_image()`:

```python
def save_image(self, image_url: str, entity_type: str, slug: str, ...):
    """Save image with null-safe slug handling."""

    # Validate slug is not None/null/empty
    if not slug or slug == "null":
        raise ValueError(
            f"Cannot save image for {entity_type}: "
            f"invalid slug '{slug}'"
        )

    # Existing sanitization
    sanitized_slug = Path(slug).name
    # ... rest of code
```

### 2. Add Better Error Handling in Generator

Update `src/generator/image_generator.py` to validate identifiers before generation:

```python
def generate_image(self, entity_type: str, slug: str, ...):
    """Generate with identifier validation."""

    # Validate identifier
    if not slug or slug == "null":
        error_msg = f"Invalid identifier for {entity_type}: '{slug}'"
        logger.error(error_msg)
        self.file_manager.update_manifest(
            entity_type, str(slug), "", False, error_msg
        )
        return

    # ... continue with generation
```

### 3. Add Retry Logic for API Errors

For JSON parsing errors like `artificer-artillerist`, add retry with exponential backoff:

```python
def _fetch_entity(self, entity_type: str, slug: str, retries: int = 3):
    """Fetch entity with retry logic."""
    for attempt in range(retries):
        try:
            response = self.session.get(url, timeout=self.timeout)
            return response.json()
        except json.JSONDecodeError as e:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Cleanup Tasks

Once API is back online:

```bash
# 1. Clean up invalid manifest entry
# Edit output/.manifest.json manually to remove sizes["null"]

# 2. Regenerate failed class
python -m src.cli --entity-type classes --slug artificer-artillerist

# 3. Investigate sizes entity
curl "http://localhost:8080/api/v1/sizes" | jq '.data'

# 4. Verify all sizes have valid identifiers
python -m src.cli --entity-type sizes --dry-run

# 5. Check final stats
cat output/.manifest.json | jq 'to_entries | map({
  entity: .key,
  failed: (.value | to_entries | map(select(.value.success == false)) | length)
}) | map(select(.failed > 0))'
```

---

**Conclusion**: Both failures are edge cases with straightforward fixes once the API is back online. The 99.7% success rate indicates the system is working well overall.
