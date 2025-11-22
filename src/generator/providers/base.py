"""Base interface for image generation providers"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class ImageProvider(ABC):
    """Abstract base class for image generation providers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration

        Args:
            config: Provider-specific configuration
        """
        self.config = config

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate an image from a text prompt

        Args:
            prompt: Text description of the image to generate

        Returns:
            URL of the generated image

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider

        Returns:
            Provider name (e.g., "dall-e", "stability-ai")
        """
        pass
