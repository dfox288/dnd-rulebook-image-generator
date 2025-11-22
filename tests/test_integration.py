"""
Integration tests for end-to-end workflow
"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.config import load_config
from src.generator.api_client import DndApiClient
from src.generator.prompt_builder import PromptBuilder
from src.generator.image_generator import ImageGenerator
from src.generator.file_manager import FileManager


@patch('src.generator.image_generator.OpenAI')
@patch('requests.get')
def test_end_to_end_spell_generation(mock_requests_get, mock_openai):
    """Test complete workflow: fetch entity -> build prompt -> generate -> save"""

    # Mock API response for entity fetch
    mock_api_response = Mock()
    mock_api_response.json.return_value = {
        "data": [{
            "slug": "fireball",
            "name": "Fireball",
            "description": "A bright streak flashes from your pointing finger",
            "school": {"name": "Evocation", "code": "EVO"}
        }],
        "meta": {"current_page": 1, "last_page": 1}
    }

    # Mock image download response
    mock_img_response = Mock()
    mock_img_response.content = b"fake_image_data"
    mock_img_response.raise_for_status = Mock()

    # Make requests.get return different responses based on the URL
    def mock_get_side_effect(url, *args, **kwargs):
        if 'api/v1' in url:
            return mock_api_response
        else:
            return mock_img_response

    mock_requests_get.side_effect = mock_get_side_effect

    # Mock DALL-E response
    mock_dalle_response = Mock()
    mock_dalle_response.data = [Mock(url="https://example.com/image.png")]
    mock_client = Mock()
    mock_client.images.generate.return_value = mock_dalle_response
    mock_openai.return_value = mock_client

    # Set up temporary output directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config
        config = {
            "api": {"base_url": "http://localhost:8080/api/v1", "timeout": 30},
            "openai": {"api_key": "test_key", "model": "dall-e-3",
                      "size": "1024x1024", "quality": "standard", "style": "vivid"},
            "output": {"base_path": tmpdir},
            "generation": {"max_retries": 3, "retry_delay": 0.1},
            "prompts": {
                "template": "Illustration of {entity_prefix} {entity}. {entityDescription}",
                "spells": {
                    "entity_prefix": "a D&D {category} spell effect:",
                    "include_category": True,
                    "category_field": "school.name",
                    "max_length": 1000
                }
            }
        }

        # Initialize components
        api_client = DndApiClient(config["api"]["base_url"], config["api"]["timeout"])
        template = config["prompts"]["template"]
        prompt_builder = PromptBuilder(config["prompts"]["spells"], "spells", template)
        image_generator = ImageGenerator(config["openai"], config["generation"])
        file_manager = FileManager(config["output"])

        # Execute workflow
        entities = list(api_client.fetch_entities("spells", limit=1))
        assert len(entities) == 1

        entity = entities[0]
        assert entity["slug"] == "fireball"

        # Build prompt
        prompt = prompt_builder.build(entity)
        assert "Evocation" in prompt
        assert "bright streak" in prompt

        # Generate image
        image_url = image_generator.generate(prompt)
        assert image_url == "https://example.com/image.png"

        # Save image
        output_path = file_manager.save_image(image_url, "spells", "fireball")
        assert Path(output_path).exists()
        assert "spells/fireball.png" in output_path

        # Update manifest (as the CLI/MCP would)
        file_manager.update_manifest("spells", "fireball", output_path, True)

        # Verify manifest
        assert file_manager.is_already_generated("spells", "fireball")
