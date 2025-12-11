#!/usr/bin/env python3
"""
Convert all PNG images in conversions directory to WebP format.

Scans output/conversions/{size}/{entity_type}/{provider}/*.png
and creates .webp versions alongside each PNG file.

WebP provides significant file size savings (typically 25-35% smaller)
while maintaining visual quality.
"""

import sys
from pathlib import Path
from PIL import Image
import logging
import argparse

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_to_webp(
    conversions_dir: Path,
    quality: int = 85,
    dry_run: bool = False
) -> dict:
    """
    Convert all PNG files in conversions directory to WebP format.

    Args:
        conversions_dir: Base conversions directory
        quality: WebP quality (0-100, default 85)
        dry_run: If True, only report what would be done

    Returns:
        Stats dict with counts and file sizes
    """
    stats = {
        "found": 0,
        "converted": 0,
        "skipped": 0,
        "errors": 0,
        "png_bytes": 0,
        "webp_bytes": 0,
        "by_size": {}
    }

    # Process each size directory (128, 256, 512)
    for size_dir in sorted(conversions_dir.iterdir()):
        if not size_dir.is_dir():
            continue
        if size_dir.name.startswith('.'):
            continue

        size_name = size_dir.name
        stats["by_size"][size_name] = {
            "found": 0,
            "converted": 0,
            "skipped": 0,
            "errors": 0,
            "png_bytes": 0,
            "webp_bytes": 0
        }

        # Process each entity type
        for entity_dir in sorted(size_dir.iterdir()):
            if not entity_dir.is_dir():
                continue

            # Process each provider directory
            for provider_dir in sorted(entity_dir.iterdir()):
                if not provider_dir.is_dir():
                    continue

                # Process all PNG files
                for png_path in sorted(provider_dir.glob("*.png")):
                    stats["found"] += 1
                    stats["by_size"][size_name]["found"] += 1

                    webp_path = png_path.with_suffix(".webp")

                    # Skip if WebP already exists
                    if webp_path.exists():
                        stats["skipped"] += 1
                        stats["by_size"][size_name]["skipped"] += 1
                        # Still count sizes for comparison
                        png_size = png_path.stat().st_size
                        webp_size = webp_path.stat().st_size
                        stats["png_bytes"] += png_size
                        stats["webp_bytes"] += webp_size
                        stats["by_size"][size_name]["png_bytes"] += png_size
                        stats["by_size"][size_name]["webp_bytes"] += webp_size
                        continue

                    if dry_run:
                        logger.debug(f"Would convert: {png_path} -> {webp_path}")
                        stats["converted"] += 1
                        stats["by_size"][size_name]["converted"] += 1
                        continue

                    try:
                        # Convert to WebP
                        with Image.open(png_path) as img:
                            img.save(webp_path, format='WEBP', quality=quality)

                        png_size = png_path.stat().st_size
                        webp_size = webp_path.stat().st_size

                        stats["png_bytes"] += png_size
                        stats["webp_bytes"] += webp_size
                        stats["by_size"][size_name]["png_bytes"] += png_size
                        stats["by_size"][size_name]["webp_bytes"] += webp_size
                        stats["converted"] += 1
                        stats["by_size"][size_name]["converted"] += 1

                    except Exception as e:
                        logger.error(f"Error converting {png_path}: {e}")
                        stats["errors"] += 1
                        stats["by_size"][size_name]["errors"] += 1

    return stats


def format_bytes(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Convert PNG images to WebP format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="WebP quality (0-100, default: 85)"
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

    logger.info(f"Converting PNG to WebP (quality={args.quality})")
    logger.info(f"Source: {args.conversions_dir}")

    stats = convert_to_webp(
        conversions_dir=args.conversions_dir,
        quality=args.quality,
        dry_run=args.dry_run
    )

    # Print summary
    print("\n" + "=" * 70)
    print("WEBP CONVERSION SUMMARY")
    print("=" * 70)
    print(f"Total PNG files found: {stats['found']}")
    print(f"Converted: {stats['converted']}")
    print(f"Skipped (already exist): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")

    if not args.dry_run and (stats['converted'] > 0 or stats['skipped'] > 0):
        print("\n" + "-" * 70)
        print("FILE SIZE COMPARISON")
        print("-" * 70)
        print(f"{'Size':<10} {'PNG':<15} {'WebP':<15} {'Savings':<15} {'%':<10}")
        print("-" * 70)

        for size_name, size_stats in sorted(stats["by_size"].items(), key=lambda x: int(x[0])):
            if size_stats["png_bytes"] > 0:
                savings = size_stats["png_bytes"] - size_stats["webp_bytes"]
                pct = (savings / size_stats["png_bytes"]) * 100
                print(f"{size_name}px{'':<6} "
                      f"{format_bytes(size_stats['png_bytes']):<15} "
                      f"{format_bytes(size_stats['webp_bytes']):<15} "
                      f"{format_bytes(savings):<15} "
                      f"{pct:.1f}%")

        print("-" * 70)
        total_savings = stats["png_bytes"] - stats["webp_bytes"]
        total_pct = (total_savings / stats["png_bytes"]) * 100 if stats["png_bytes"] > 0 else 0
        print(f"{'TOTAL':<10} "
              f"{format_bytes(stats['png_bytes']):<15} "
              f"{format_bytes(stats['webp_bytes']):<15} "
              f"{format_bytes(total_savings):<15} "
              f"{total_pct:.1f}%")
        print("=" * 70)

    if args.dry_run:
        print("\nDRY RUN - No changes were made")

    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
