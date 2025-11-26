#!/usr/bin/env python3
"""
Batch converter to create 128x128 versions of all existing images.

This script scans all provider directories under output/{entity_type}/{provider}/
and creates 128px conversions in output/conversions/128/{entity_type}/{provider}/
"""

import sys
from pathlib import Path
from PIL import Image
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_images(
    output_dir: Path,
    conversions_dir: Path,
    target_size: int = 128,
    dry_run: bool = False
) -> dict:
    """
    Convert all images to target size.

    Args:
        output_dir: Base output directory containing entity_type/provider/images
        conversions_dir: Base conversions directory
        target_size: Target size in pixels (default 128)
        dry_run: If True, only report what would be done

    Returns:
        Stats dict with counts
    """
    stats = {
        "found": 0,
        "converted": 0,
        "skipped": 0,
        "errors": 0,
        "by_entity_type": {}
    }

    # Find all entity type directories
    for entity_dir in sorted(output_dir.iterdir()):
        if not entity_dir.is_dir():
            continue
        if entity_dir.name.startswith('.'):
            continue
        if entity_dir.name == 'conversions':
            continue

        entity_type = entity_dir.name
        stats["by_entity_type"][entity_type] = {"converted": 0, "skipped": 0, "errors": 0}

        # Find provider directories (e.g., stability-ai, dall-e)
        for provider_dir in sorted(entity_dir.iterdir()):
            if not provider_dir.is_dir():
                continue

            provider_name = provider_dir.name

            # Create target directory
            target_dir = conversions_dir / str(target_size) / entity_type / provider_name

            # Process all PNG files
            for image_path in sorted(provider_dir.glob("*.png")):
                stats["found"] += 1

                target_path = target_dir / image_path.name

                # Skip if already exists
                if target_path.exists():
                    stats["skipped"] += 1
                    stats["by_entity_type"][entity_type]["skipped"] += 1
                    continue

                if dry_run:
                    logger.info(f"Would convert: {image_path} -> {target_path}")
                    stats["converted"] += 1
                    stats["by_entity_type"][entity_type]["converted"] += 1
                    continue

                try:
                    # Ensure target directory exists
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Open and resize
                    with Image.open(image_path) as img:
                        resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
                        resized.save(target_path, format='PNG')

                    stats["converted"] += 1
                    stats["by_entity_type"][entity_type]["converted"] += 1

                except Exception as e:
                    logger.error(f"Error converting {image_path}: {e}")
                    stats["errors"] += 1
                    stats["by_entity_type"][entity_type]["errors"] += 1

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch convert images to 128x128 size"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=128,
        help="Target size in pixels (default: 128)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=project_root / "output",
        help="Base output directory (default: ./output)"
    )
    parser.add_argument(
        "--conversions-dir",
        type=Path,
        default=project_root / "output" / "conversions",
        help="Conversions directory (default: ./output/conversions)"
    )

    args = parser.parse_args()

    if args.dry_run:
        logger.info("DRY RUN - No changes will be made")

    logger.info(f"Converting images to {args.size}x{args.size}")
    logger.info(f"Source: {args.output_dir}")
    logger.info(f"Target: {args.conversions_dir}/{args.size}/")

    stats = convert_images(
        output_dir=args.output_dir,
        conversions_dir=args.conversions_dir,
        target_size=args.size,
        dry_run=args.dry_run
    )

    # Print summary
    print("\n" + "=" * 50)
    print("CONVERSION SUMMARY")
    print("=" * 50)
    print(f"Total images found: {stats['found']}")
    print(f"Converted: {stats['converted']}")
    print(f"Skipped (already exist): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print()
    print("By entity type:")
    for entity_type, entity_stats in sorted(stats["by_entity_type"].items()):
        total = entity_stats["converted"] + entity_stats["skipped"] + entity_stats["errors"]
        if total > 0:
            print(f"  {entity_type}: {entity_stats['converted']} converted, "
                  f"{entity_stats['skipped']} skipped, {entity_stats['errors']} errors")

    if args.dry_run:
        print("\nDRY RUN - No changes were made")

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
