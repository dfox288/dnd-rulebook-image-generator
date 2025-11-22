import pytest
from src.generator.prompt_builder import PromptBuilder


def test_build_prompt_without_category():
    """Test building prompt without category using template"""
    config = {
        "entity_prefix": "a D&D",
        "include_category": False,
        "max_length": 1000
    }

    template = "Illustration of {entity_prefix} {entity}. {entityDescription}"

    entity = {
        "name": "Wizard",
        "description": "Masters of arcane magic"
    }

    builder = PromptBuilder(config, "classes", template)
    prompt = builder.build(entity)

    assert prompt == "Illustration of a D&D Wizard. Masters of arcane magic"


def test_build_prompt_with_category():
    """Test building prompt with category extraction using template"""
    config = {
        "entity_prefix": "a D&D {category} spell effect:",
        "include_category": True,
        "category_field": "school.name",
        "max_length": 1000
    }

    template = "Illustration of {entity_prefix} {entity}. {entityDescription} Magical effects."

    entity = {
        "name": "Fireball",
        "description": "A blast of fire",
        "school": {"name": "Evocation", "code": "EVO"}
    }

    builder = PromptBuilder(config, "spells", template)
    prompt = builder.build(entity)

    assert prompt == "Illustration of a D&D Evocation spell effect: Fireball. A blast of fire Magical effects."


def test_build_prompt_truncates_at_sentence():
    """Test that long descriptions are truncated at sentence boundaries"""
    config = {
        "entity_prefix": "a",
        "include_category": False,
        "max_length": 50
    }

    template = "{entity_prefix} {entity}. {entityDescription}"

    entity = {
        "name": "Magic Sword",
        "description": "This is a very long description that exceeds the limit. This is another sentence. And another."
    }

    builder = PromptBuilder(config, "items", template)
    prompt = builder.build(entity)

    # Should truncate at sentence boundary
    assert len(prompt) <= 50


def test_build_prompt_with_custom_text():
    """Test building prompt with custom text override"""
    config = {
        "entity_prefix": "a",
        "include_category": False,
        "max_length": 1000
    }

    template = "{entity_prefix} {entity}. {entityDescription}"

    entity = {"name": "Sword", "description": "Normal sword"}

    builder = PromptBuilder(config, "items", template)
    prompt = builder.build(entity, custom_text="ancient elven blade with runes")

    assert "ancient elven blade with runes" in prompt
    assert "Normal sword" not in prompt


def test_extract_flavor_text_spells():
    """Test flavor text extraction for spells"""
    entity = {
        "name": "Magic Missile",
        "description": "You create three glowing darts of magical force.",
        "higher_levels": "When you cast this spell using a spell slot of 2nd level or higher."
    }

    config = {"entity_prefix": "a", "include_category": False, "max_length": 1000}
    builder = PromptBuilder(config, "spells", "")

    flavor = builder._extract_flavor_text(entity)

    assert "You create three glowing darts" in flavor


def test_extract_category_nested_field():
    """Test extracting category from nested field"""
    entity = {
        "name": "Longsword",
        "item_type": {"name": "Weapon", "code": "W"}
    }

    config = {
        "entity_prefix": "a D&D {category} item:",
        "include_category": True,
        "category_field": "item_type.name",
        "max_length": 1000
    }

    builder = PromptBuilder(config, "items", "")
    category = builder._extract_category(entity)

    assert category == "Weapon"


def test_build_prompt_with_empty_description():
    """Test building prompt when entity has empty description"""
    config = {
        "entity_prefix": "a",
        "include_category": False,
        "max_length": 1000
    }

    template = "{entity_prefix} {entity}. {entityDescription} Fantasy art."

    entity = {
        "name": "Unknown Item",
        "description": ""
    }

    builder = PromptBuilder(config, "items", template)
    prompt = builder.build(entity)

    # Should still build a valid prompt
    assert "Unknown Item" in prompt
    assert "Fantasy art" in prompt


def test_build_prompt_with_template():
    """Test building prompt with full template"""
    config = {
        "entity_prefix": "a",
        "include_category": False,
        "max_length": 1000
    }

    template = "A whimsical illustration of {entity_prefix} {entity}. {entityDescription} Storybook art style."

    entity = {
        "name": "Elf",
        "description": "Graceful forest dweller"
    }

    builder = PromptBuilder(config, "races", template)
    prompt = builder.build(entity)

    assert prompt == "A whimsical illustration of a Elf. Graceful forest dweller Storybook art style."
