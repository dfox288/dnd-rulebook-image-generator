from typing import Dict, Any, Optional
import re


class PromptBuilder:
    """Builds DALL-E prompts from entity data and configuration using template system"""

    def __init__(self, config: Dict[str, Any], entity_type: str, template: str = ""):
        self.config = config
        self.entity_type = entity_type
        self.template = template

    def build(self, entity: Dict[str, Any], custom_text: Optional[str] = None) -> str:
        """
        Build a prompt for DALL-E from entity data using template

        Args:
            entity: Entity data from API
            custom_text: Optional custom text to override flavor text

        Returns:
            Formatted prompt string
        """
        max_length = self.config.get("max_length", 1000)

        # Get entity name
        entity_name = entity.get("name", "")

        # Get entity prefix (e.g., "a", "a D&D Evocation spell effect:")
        entity_prefix = self.config.get("entity_prefix", "")

        # Extract category if configured
        if self.config.get("include_category", False):
            category = self._extract_category(entity)
            entity_prefix = entity_prefix.replace("{category}", category)
            # Normalize whitespace to prevent double spaces when category is empty
            entity_prefix = re.sub(r'\s+', ' ', entity_prefix).strip()

        # Get description text
        if custom_text:
            entity_description = custom_text
        else:
            entity_description = self._extract_flavor_text(entity)

        # Filter out bad/confusing descriptions
        entity_description = self._clean_description(entity_description)

        # Build prompt from template
        if self.template:
            prompt = self.template.replace("{entity_prefix}", entity_prefix)
            prompt = prompt.replace("{entity}", entity_name)
            prompt = prompt.replace("{entityDescription}", entity_description)
        else:
            # Fallback to simple concatenation if no template
            prompt = f"{entity_prefix} {entity_name}. {entity_description}"

        # Truncate if needed
        if len(prompt) > max_length:
            prompt = self._truncate_at_sentence(prompt, max_length)

        return prompt

    def _extract_flavor_text(self, entity: Dict[str, Any]) -> str:
        """Extract descriptive flavor text from entity"""
        # Primary source: description field
        description = entity.get("description") or ""

        # TODO: Consider adding higher_levels text for spells if description is too short
        # Currently only using description as higher_levels is too mechanical for image generation

        return description.strip()

    def _clean_description(self, description: str) -> str:
        """
        Clean and filter descriptions that might confuse DALL-E

        Removes:
        - "NO DESCRIPTION" placeholder text
        - "Source:" attribution lines
        - Very short/empty descriptions

        Returns empty string if description is invalid/confusing
        """
        if not description:
            return ""

        # Remove "NO DESCRIPTION" placeholder
        if description.upper() == "NO DESCRIPTION":
            return ""

        # Remove "Source:" lines from item descriptions
        lines = description.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Skip source attribution lines
            if line.startswith("Source:") or line.startswith("source:"):
                continue
            cleaned_lines.append(line)

        cleaned = ' '.join(cleaned_lines).strip()

        # If description is too short (< 20 chars), it's probably not useful
        if len(cleaned) < 20:
            return ""

        return cleaned

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
