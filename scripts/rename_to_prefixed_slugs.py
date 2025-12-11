#!/usr/bin/env python3
"""
Rename image files to match new prefixed slug format from API.

The API now returns slugs like "phb:acid-splash" instead of "acid-splash".
Since colons are problematic in filenames on macOS, we use "--" as separator.

Example: acid-splash.png -> phb--acid-splash.png
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Tuple

# Entity types that use /lookups/ prefix
LOOKUP_ENTITY_TYPES = {
    'sources', 'spell_schools', 'damage_types', 'sizes', 'ability_scores',
    'skills', 'item_types', 'item_properties', 'conditions', 'proficiency_types', 'languages'
}

# All entity types we have images for
ALL_ENTITY_TYPES = [
    'spells', 'items', 'classes', 'races', 'backgrounds', 'monsters', 'feats',
    'item_types', 'languages', 'sizes', 'spell_schools', 'ability_scores',
    'conditions', 'damage_types', 'item_properties', 'proficiency_types', 'skills', 'sources'
]

API_BASE = "http://localhost:8080/api/v1"
OUTPUT_BASE = Path("/Users/dfox/Development/ledger-of-heroes/image-generator/output")


def get_api_endpoint(entity_type: str) -> str:
    """Get the correct API endpoint for an entity type."""
    # Convert underscores to hyphens for API paths
    api_path = entity_type.replace('_', '-')
    if entity_type in LOOKUP_ENTITY_TYPES:
        return f"{API_BASE}/lookups/{api_path}"
    return f"{API_BASE}/{api_path}"


def fetch_all_slugs(entity_type: str) -> Dict[str, str]:
    """
    Fetch all entities and return mapping of old slug (without prefix) to new slug (full).
    Returns: {old_slug: new_slug} e.g., {"acid-splash": "phb--acid-splash"}
    """
    endpoint = get_api_endpoint(entity_type)
    mapping = {}
    page = 1
    per_page = 100

    while True:
        try:
            response = requests.get(
                endpoint,
                params={"page": page, "per_page": per_page},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            # Handle both paginated and non-paginated responses
            items = data.get('data', data) if isinstance(data, dict) else data

            for item in items:
                # Main entities have 'slug', lookup entities have 'code' or just 'id'
                new_slug = item.get('slug')

                # Skip entities without slug field (lookup entities use code/id)
                if new_slug is None:
                    code = item.get('code')
                    if code:
                        # Lookup entity with code - no rename needed
                        mapping[str(code)] = str(code)
                    continue

                # Convert to string in case it's not
                new_slug = str(new_slug)

                if ':' in new_slug:
                    # Extract old slug (part after colon) and create mapping
                    prefix, old_slug = new_slug.split(':', 1)
                    # Use -- as separator for filename
                    filename_slug = f"{prefix}--{old_slug}"
                    mapping[old_slug] = filename_slug
                else:
                    # No prefix, keep as-is
                    mapping[new_slug] = new_slug

            # Check if there are more pages
            if isinstance(data, dict) and 'meta' in data:
                meta = data['meta']
                if page >= meta.get('last_page', 1):
                    break
            else:
                break

            page += 1

        except requests.RequestException as e:
            print(f"  Error fetching {entity_type}: {e}")
            break

    return mapping


def find_files_to_rename(entity_type: str, slug_mapping: Dict[str, str]) -> List[Tuple[Path, Path]]:
    """
    Find all files that need renaming for an entity type.
    Returns list of (old_path, new_path) tuples.
    """
    renames = []

    # Check PNG originals
    png_dir = OUTPUT_BASE / entity_type / "stability-ai"
    if png_dir.exists():
        for png_file in png_dir.glob("*.png"):
            old_slug = png_file.stem
            if old_slug in slug_mapping:
                new_slug = slug_mapping[old_slug]
                if old_slug != new_slug:  # Only if actually different
                    new_path = png_file.parent / f"{new_slug}.png"
                    renames.append((png_file, new_path))

    # Check conversions (128, 256, 512) - both webp and png files
    for size in ['128', '256', '512']:
        conv_dir = OUTPUT_BASE / "conversions" / size / entity_type / "stability-ai"
        if conv_dir.exists():
            # Check both .webp and .png files
            for ext in ['*.webp', '*.png']:
                for conv_file in conv_dir.glob(ext):
                    old_slug = conv_file.stem
                    if old_slug in slug_mapping:
                        new_slug = slug_mapping[old_slug]
                        if old_slug != new_slug:
                            new_path = conv_file.parent / f"{new_slug}{conv_file.suffix}"
                            renames.append((conv_file, new_path))

    return renames


def main():
    dry_run = "--dry-run" in sys.argv

    if dry_run:
        print("=== DRY RUN - No files will be renamed ===\n")

    total_renames = 0
    total_missing = 0

    for entity_type in ALL_ENTITY_TYPES:
        print(f"\n{'='*60}")
        print(f"Processing: {entity_type}")
        print(f"{'='*60}")

        # Fetch slug mapping from API
        print(f"  Fetching slugs from API...")
        slug_mapping = fetch_all_slugs(entity_type)
        print(f"  Found {len(slug_mapping)} entities in API")

        # Find files to rename
        renames = find_files_to_rename(entity_type, slug_mapping)

        if not renames:
            print(f"  No files need renaming")
            continue

        print(f"  Files to rename: {len(renames)}")

        # Track files that exist in filesystem but not in API
        existing_files = set()
        png_dir = OUTPUT_BASE / entity_type / "stability-ai"
        if png_dir.exists():
            existing_files.update(f.stem for f in png_dir.glob("*.png"))

        missing_from_api = existing_files - set(slug_mapping.keys())
        if missing_from_api:
            print(f"  WARNING: {len(missing_from_api)} files not found in API:")
            for slug in sorted(missing_from_api)[:5]:
                print(f"    - {slug}")
            if len(missing_from_api) > 5:
                print(f"    ... and {len(missing_from_api) - 5} more")
            total_missing += len(missing_from_api)

        # Perform renames
        renamed_count = 0
        for old_path, new_path in renames:
            if dry_run:
                print(f"  Would rename: {old_path.name} -> {new_path.name}")
            else:
                try:
                    old_path.rename(new_path)
                    renamed_count += 1
                except OSError as e:
                    print(f"  Error renaming {old_path}: {e}")

        if not dry_run:
            print(f"  Renamed {renamed_count} files")

        total_renames += len(renames)

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total files to rename: {total_renames}")
    print(f"Files not found in API: {total_missing}")

    if dry_run:
        print(f"\nRun without --dry-run to perform the renames")


if __name__ == "__main__":
    main()
