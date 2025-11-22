"""DALL-E image generation provider"""
import time
import logging
from typing import Dict, Any
from openai import OpenAI

from .base import ImageProvider

logger = logging.getLogger(__name__)


class DalleProvider(ImageProvider):
    """Image generation using OpenAI's DALL-E API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.client = OpenAI(api_key=config["api_key"])
        self.model = config.get("model", "dall-e-3")
        self.size = config.get("size", "1024x1024")
        self.quality = config.get("quality", "standard")
        self.style = config.get("style", "vivid")

        # Retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 5)

    def generate(self, prompt: str) -> str:
        """
        Generate an image using DALL-E

        Args:
            prompt: Text description for image generation

        Returns:
            URL of generated image

        Raises:
            Exception: If generation fails after all retries
        """
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.images.generate(
                    model=self.model,
                    prompt=prompt,
                    size=self.size,
                    quality=self.quality,
                    style=self.style,
                    n=1
                )

                return response.data[0].url

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"DALL-E generation attempt {attempt + 1} failed: {e}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"DALL-E generation failed after {self.max_retries} retries: {e}")
                    raise

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "dall-e"
