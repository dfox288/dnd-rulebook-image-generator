import pytest
from unittest.mock import Mock, patch, MagicMock
from src.generator.image_generator import ImageGenerator


@patch('src.generator.image_generator.OpenAI')
def test_generate_image_success(mock_openai_class):
    """Test successful image generation"""
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    mock_response = Mock()
    mock_response.data = [Mock(url="https://example.com/image.png")]
    mock_client.images.generate.return_value = mock_response

    config = {
        "model": "dall-e-3",
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid",
        "api_key": "test_key"
    }

    generator = ImageGenerator(config)
    image_url = generator.generate("A fantasy dragon")

    assert image_url == "https://example.com/image.png"
    mock_client.images.generate.assert_called_once()


@patch('src.generator.image_generator.OpenAI')
def test_generate_image_with_retry(mock_openai_class):
    """Test retry logic on rate limit"""
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    # First call fails, second succeeds
    mock_response = Mock()
    mock_response.data = [Mock(url="https://example.com/image.png")]

    mock_client.images.generate.side_effect = [
        Exception("Rate limit exceeded"),
        mock_response
    ]

    config = {
        "model": "dall-e-3",
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid",
        "api_key": "test_key"
    }

    retry_config = {"max_retries": 3, "retry_delay": 0.1}
    generator = ImageGenerator(config, retry_config)

    image_url = generator.generate("A fantasy dragon")

    assert image_url == "https://example.com/image.png"
    assert mock_client.images.generate.call_count == 2


@patch('src.generator.image_generator.OpenAI')
def test_generate_image_max_retries_exceeded(mock_openai_class):
    """Test that max retries are respected"""
    mock_client = Mock()
    mock_openai_class.return_value = mock_client

    mock_client.images.generate.side_effect = Exception("Rate limit exceeded")

    config = {
        "model": "dall-e-3",
        "size": "1024x1024",
        "quality": "standard",
        "style": "vivid",
        "api_key": "test_key"
    }

    retry_config = {"max_retries": 2, "retry_delay": 0.1}
    generator = ImageGenerator(config, retry_config)

    with pytest.raises(Exception, match="Rate limit exceeded"):
        generator.generate("A fantasy dragon")

    assert mock_client.images.generate.call_count == 3  # Initial + 2 retries
