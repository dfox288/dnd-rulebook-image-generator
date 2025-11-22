import time
import logging
from typing import Dict, Any, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)


class ImageGenerator:
    """Generates images using OpenAI's DALL-E API"""

    def __init__(
        self,
        openai_config: Dict[str, Any],
        retry_config: Optional[Dict[str, Any]] = None
    ):
        self.config = openai_config
        self.retry_config = retry_config or {"max_retries": 3, "retry_delay": 5}

        self.client = OpenAI(api_key=openai_config["api_key"])
        self.model = openai_config.get("model", "dall-e-3")
        self.size = openai_config.get("size", "1024x1024")
        self.quality = openai_config.get("quality", "standard")
        self.style = openai_config.get("style", "vivid")

    def generate(self, prompt: str) -> str:
        """
        Generate an image from a text prompt

        Args:
            prompt: Text description for image generation

        Returns:
            URL of generated image

        Raises:
            Exception: If generation fails after all retries
        """
        max_retries = self.retry_config.get("max_retries", 3)
        retry_delay = self.retry_config.get("retry_delay", 5)

        for attempt in range(max_retries + 1):
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
                if attempt < max_retries:
                    logger.warning(f"Image generation attempt {attempt + 1} failed: {e}")
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Image generation failed after {max_retries} retries: {e}")
                    raise
