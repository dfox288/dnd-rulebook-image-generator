#!/usr/bin/env python3
"""
MCP server for Claude Code integration
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging
from typing import Optional
from dotenv import load_dotenv
from mcp.server import FastMCP

from src.config import load_config, get_prompt_config
from src.generator.api_client import DndApiClient
from src.generator.prompt_builder import PromptBuilder
from src.generator.image_generator import ImageGenerator
from src.generator.file_manager import FileManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

# Initialize components
config = load_config()
api_client = DndApiClient(
    base_url=config["api"]["base_url"],
    timeout=config["api"]["timeout"]
)
image_generator = ImageGenerator(config["openai"], config["generation"])
file_manager = FileManager(config["output"])

# Create MCP server
app = FastMCP("dnd-image-generator")


@app.tool()
async def generate_image(
    entity_type: str,
    slug: str,
    custom_prompt: Optional[str] = None
) -> str:
    """
    Generate an image for a specific D&D entity

    Args:
        entity_type: Type of entity (spells, items, classes, races, backgrounds)
        slug: Entity slug identifier
        custom_prompt: Optional custom text to override default flavor text

    Returns:
        Path to generated image
    """
    try:
        # Fetch entity
        logger.info(f"Fetching {entity_type}/{slug}...")
        entities = [e for e in api_client.fetch_entities(entity_type, limit=100)
                   if e.get('slug') == slug]

        if not entities:
            return f"Error: Entity '{slug}' not found in {entity_type}"

        entity = entities[0]

        # Build prompt
        prompt_config = get_prompt_config(config, entity_type)
        prompt_builder = PromptBuilder(prompt_config, entity_type)
        prompt = prompt_builder.build(entity, custom_text=custom_prompt)

        logger.info(f"Generating image with prompt: {prompt[:100]}...")

        # Generate image
        image_url = image_generator.generate(prompt)

        # Save image
        output_path = file_manager.save_image(image_url, entity_type, slug)

        # Update manifest
        file_manager.update_manifest(entity_type, slug, output_path, True)

        return f"Successfully generated image: {output_path}"

    except Exception as e:
        logger.error(f"Failed to generate image: {e}")
        return f"Error: {str(e)}"


@app.tool()
async def batch_generate(
    entity_type: str,
    limit: Optional[int] = None
) -> str:
    """
    Batch generate images for multiple entities

    Args:
        entity_type: Type of entity (spells, items, classes, races, backgrounds)
        limit: Optional limit on number of entities to process

    Returns:
        Summary of generation results
    """
    try:
        # Fetch entities
        logger.info(f"Fetching {entity_type}...")
        entities = list(api_client.fetch_entities(entity_type, limit=limit))

        prompt_config = get_prompt_config(config, entity_type)
        prompt_builder = PromptBuilder(prompt_config, entity_type)

        success_count = 0
        error_count = 0
        skip_count = 0

        for entity in entities:
            slug = entity.get('slug')

            # Skip if already generated
            if file_manager.is_already_generated(entity_type, slug):
                skip_count += 1
                continue

            try:
                # Build and generate
                prompt = prompt_builder.build(entity)
                image_url = image_generator.generate(prompt)
                output_path = file_manager.save_image(image_url, entity_type, slug)
                file_manager.update_manifest(entity_type, slug, output_path, True)

                success_count += 1
                logger.info(f"Generated {slug}")

            except Exception as e:
                logger.error(f"Failed to generate {slug}: {e}")
                file_manager.update_manifest(entity_type, slug, "", False, str(e))
                error_count += 1

        return f"Batch generation complete: {success_count} succeeded, {skip_count} skipped, {error_count} failed"

    except Exception as e:
        logger.error(f"Batch generation failed: {e}")
        return f"Error: {str(e)}"


@app.tool()
async def list_generated(entity_type: Optional[str] = None) -> str:
    """
    List generated images

    Args:
        entity_type: Optional filter by entity type

    Returns:
        Summary of generated images
    """
    try:
        count = file_manager.get_generated_count(entity_type)

        if entity_type:
            return f"Generated {count} images for {entity_type}"
        else:
            return f"Generated {count} total images"

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == '__main__':
    import asyncio

    # Run MCP server
    logger.info("Starting D&D Image Generator MCP server...")
    app.run()
