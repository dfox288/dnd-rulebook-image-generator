from typing import Dict, Any, Optional
import re


class PromptBuilder:
    """Builds DALL-E prompts from entity data and configuration"""

    def __init__(self, config: Dict[str, Any], entity_type: str):
        self.config = config
        self.entity_type = entity_type

    def build(self, entity: Dict[str, Any], custom_text: Optional[str] = None) -> str:
        """
        Build a prompt for DALL-E from entity data

        Args:
            entity: Entity data from API
            custom_text: Optional custom text to override flavor text

        Returns:
            Formatted prompt string
        """
        prefix = self.config.get("prefix", "")
        suffix = self.config.get("suffix", "")
        max_length = self.config.get("max_length", 1000)

        # Extract category if configured
        if self.config.get("include_category", False):
            category = self._extract_category(entity)
            prefix = prefix.replace("{category}", category)
            # Normalize whitespace to prevent double spaces when category is empty
            prefix = re.sub(r'\s+', ' ', prefix)

        # Get flavor text
        if custom_text:
            flavor_text = custom_text
        else:
            flavor_text = self._extract_flavor_text(entity)

        # Assemble prompt
        prompt = f"{prefix}{flavor_text}{suffix}"

        # Truncate if needed
        if len(prompt) > max_length:
            prompt = self._truncate_at_sentence(prompt, max_length)

        return prompt

    def _extract_flavor_text(self, entity: Dict[str, Any]) -> str:
        """Extract descriptive flavor text from entity"""
        # Primary source: description field
        description = entity.get("description", "")

        # TODO: Consider adding higher_levels text for spells if description is too short
        # Currently only using description as higher_levels is too mechanical for image generation

        return description.strip()

    def _extract_category(self, entity: Dict[str, Any]) -> str:
        """Extract category value from nested field path"""
        category_field = self.config.get("category_field", "")

        if not category_field:
            return ""

        # Handle nested paths like "item_type.name"
        parts = category_field.split(".")
        value = entity

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return ""

        return str(value)

    def _truncate_at_sentence(self, text: str, max_length: int) -> str:
        """Truncate text at sentence boundary before max_length"""
        if len(text) <= max_length:
            return text

        # Find the last sentence ending before max_length
        truncated = text[:max_length]

        # Look for sentence endings (., !, ?)
        sentence_ends = [m.end() for m in re.finditer(r'[.!?]\s+', truncated)]

        if sentence_ends:
            last_sentence_end = sentence_ends[-1]
            return text[:last_sentence_end].strip()

        # If no sentence boundary found, just truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space].strip() + "..."

        return truncated + "..."
