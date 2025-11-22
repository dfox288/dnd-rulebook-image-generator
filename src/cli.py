#!/usr/bin/env python3
"""
CLI script for batch image generation
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

from src.config import load_config, get_prompt_config
from src.generator.api_client import DndApiClient
from src.generator.prompt_builder import PromptBuilder
from src.generator.providers.factory import create_provider
from src.generator.file_manager import FileManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Load environment variables
    load_dotenv()

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate D&D entity images using DALL-E')
    parser.add_argument('--entity-type', required=True,
                       choices=['spells', 'items', 'classes', 'races', 'backgrounds'],
                       help='Type of entity to generate images for')
    parser.add_argument('--limit', type=int, help='Limit number of entities to process')
    parser.add_argument('--slug', help='Generate image for specific entity slug')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview what would be generated without calling DALL-E')
    parser.add_argument('--force-regenerate', action='store_true',
                       help='Regenerate images even if they already exist')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')

    args = parser.parse_args()

    # Load configuration
    try:
        config = load_config(args.config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(1)

    # Initialize components
    api_client = DndApiClient(
        base_url=config["api"]["base_url"],
        timeout=config["api"]["timeout"]
    )

    prompt_config = get_prompt_config(config, args.entity_type)
    # Use entity-specific template if available, otherwise use global template
    template = prompt_config.get("template") or config.get("prompts", {}).get("template", "")
    prompt_builder = PromptBuilder(prompt_config, args.entity_type, template)

    file_manager = FileManager(config["output"])

    if not args.dry_run:
        # Get provider type and config
        provider_type = config["image_generation"]["provider"]
        provider_config = config["image_generation"][provider_type]

        logger.info(f"Using image provider: {provider_type}")
        image_provider = create_provider(provider_type, provider_config)

    # Fetch entities
    logger.info(f"Fetching {args.entity_type}...")

    if args.slug:
        # Fetch all and filter by slug (API doesn't support direct slug lookup)
        entities = [e for e in api_client.fetch_entities(args.entity_type, limit=1000)
                   if e.get('slug') == args.slug]
        if not entities:
            logger.error(f"Entity with slug '{args.slug}' not found")
            sys.exit(1)
    else:
        entities = list(api_client.fetch_entities(args.entity_type, limit=args.limit))

    logger.info(f"Found {len(entities)} entities")

    # Process entities
    success_count = 0
    skip_count = 0
    error_count = 0

    batch_delay = config["generation"].get("batch_delay", 2)

    for idx, entity in enumerate(entities, 1):
        slug = entity.get('slug')
        name = entity.get('name', slug)

        logger.info(f"[{idx}/{len(entities)}] Processing: {name} ({slug})")

        # Skip if already generated
        if not args.force_regenerate and file_manager.is_already_generated(args.entity_type, slug):
            logger.info(f"  Skipping (already generated)")
            skip_count += 1
            continue

        # Build prompt
        try:
            prompt = prompt_builder.build(entity)
            logger.info(f"  Prompt: {prompt[:100]}...")

            if args.dry_run:
                logger.info(f"  [DRY RUN] Would generate image")
                success_count += 1
                continue

            # Generate image
            image_url = image_provider.generate(prompt)

            # Save image with provider name in filename
            provider_name = image_provider.get_provider_name()
            output_path = file_manager.save_image(image_url, args.entity_type, slug, provider_name)

            # Update manifest
            file_manager.update_manifest(args.entity_type, slug, output_path, True)

            logger.info(f"  ✓ Generated: {output_path}")
            success_count += 1

            # Rate limiting
            if idx < len(entities):
                time.sleep(batch_delay)

        except Exception as e:
            logger.error(f"  ✗ Failed: {e}")
            file_manager.update_manifest(args.entity_type, slug, "", False, str(e))
            error_count += 1

    # Summary
    logger.info("\n" + "="*50)
    logger.info("GENERATION SUMMARY")
    logger.info("="*50)
    logger.info(f"Total entities: {len(entities)}")
    logger.info(f"Successfully generated: {success_count}")
    logger.info(f"Skipped (already exist): {skip_count}")
    logger.info(f"Failed: {error_count}")

    if not args.dry_run:
        estimated_cost = success_count * 0.04
        logger.info(f"Estimated cost: ${estimated_cost:.2f}")


if __name__ == '__main__':
    main()
