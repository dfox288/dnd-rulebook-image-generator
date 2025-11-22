"""Factory for creating image generation providers"""
from typing import Dict, Any
from .base import ImageProvider
from .dalle_provider import DalleProvider
from .stability_provider import StabilityProvider


def create_provider(provider_type: str, config: Dict[str, Any]) -> ImageProvider:
    """
    Create an image generation provider

    Args:
        provider_type: Type of provider ("dall-e" or "stability-ai")
        config: Provider-specific configuration

    Returns:
        ImageProvider instance

    Raises:
        ValueError: If provider_type is not supported
    """
    providers = {
        "dall-e": DalleProvider,
        "stability-ai": StabilityProvider,
    }

    provider_class = providers.get(provider_type)

    if not provider_class:
        available = ", ".join(providers.keys())
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Available providers: {available}"
        )

    return provider_class(config)
