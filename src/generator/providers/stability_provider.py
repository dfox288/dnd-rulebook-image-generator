"""Stability.ai image generation provider"""
import time
import logging
import requests
from typing import Dict, Any, List

from .base import ImageProvider

logger = logging.getLogger(__name__)


class StabilityProvider(ImageProvider):
    """Image generation using Stability.ai API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

        self.api_key = config["api_key"]
        self.model = config.get("model", "stable-diffusion-xl-1024-v1-0")
        self.base_url = config.get("base_url", "https://api.stability.ai/v1/generation")

        # Image generation parameters
        self.width = config.get("width", 1024)
        self.height = config.get("height", 1024)
        self.cfg_scale = config.get("cfg_scale", 7)
        self.steps = config.get("steps", 30)
        self.samples = config.get("samples", 1)

        # Retry configuration
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 5)

    def generate(self, prompt: str, negative_prompt: str = "") -> str:
        """
        Generate an image using Stability.ai

        Args:
            prompt: Text description for image generation
            negative_prompt: Things to avoid in the image

        Returns:
            URL of generated image (base64 data URL)

        Raises:
            Exception: If generation fails after all retries
        """
        # Build text prompts with weights
        text_prompts = [{"text": prompt, "weight": 1}]

        if negative_prompt:
            text_prompts.append({"text": negative_prompt, "weight": -1})

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    f"{self.base_url}/{self.model}/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    json={
                        "text_prompts": text_prompts,
                        "cfg_scale": self.cfg_scale,
                        "height": self.height,
                        "width": self.width,
                        "steps": self.steps,
                        "samples": self.samples,
                    },
                    timeout=60
                )

                response.raise_for_status()

                data = response.json()

                # Stability.ai returns base64 encoded images
                # We need to return a data URL that can be "downloaded" by file_manager
                if data.get("artifacts") and len(data["artifacts"]) > 0:
                    base64_image = data["artifacts"][0]["base64"]
                    # Return as data URL
                    return f"data:image/png;base64,{base64_image}"
                else:
                    raise ValueError("No image returned from Stability.ai")

            except Exception as e:
                if attempt < self.max_retries:
                    logger.warning(f"Stability.ai generation attempt {attempt + 1} failed: {e}")
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"Stability.ai generation failed after {self.max_retries} retries: {e}")
                    raise

    def get_provider_name(self) -> str:
        """Get provider name"""
        return "stability-ai"
