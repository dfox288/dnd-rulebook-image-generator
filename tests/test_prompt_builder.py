import pytest
from src.generator.prompt_builder import PromptBuilder


def test_build_prompt_without_category():
    """Test building prompt without category"""
    config = {
        "prefix": "D&D character: ",
        "suffix": ". Heroic pose.",
        "include_category": False,
        "max_length": 1000
    }

    entity = {
        "name": "Wizard",
        "description": "Masters of arcane magic"
    }

    builder = PromptBuilder(config, "classes")
    prompt = builder.build(entity)

    assert prompt == "D&D character: Masters of arcane magic. Heroic pose."


def test_build_prompt_with_category():
    """Test building prompt with category extraction"""
    config = {
        "prefix": "D&D {category} spell: ",
        "suffix": ". Magical effects.",
        "include_category": True,
        "category_field": "school.name",
        "max_length": 1000
    }

    entity = {
        "name": "Fireball",
        "description": "A blast of fire",
        "school": {"name": "Evocation", "code": "EVO"}
    }

    builder = PromptBuilder(config, "spells")
    prompt = builder.build(entity)

    assert prompt == "D&D Evocation spell: A blast of fire. Magical effects."


def test_build_prompt_truncates_at_sentence():
    """Test that long descriptions are truncated at sentence boundaries"""
    config = {
        "prefix": "Item: ",
        "suffix": ".",
        "include_category": False,
        "max_length": 50
    }

    entity = {
        "name": "Magic Sword",
        "description": "This is a very long description that exceeds the limit. This is another sentence. And another."
    }

    builder = PromptBuilder(config, "items")
    prompt = builder.build(entity)

    # Should truncate at sentence boundary
    assert len(prompt) <= 50
    assert not prompt.endswith("exceeds the limit.")  # Truncated before max


def test_build_prompt_with_custom_text():
    """Test building prompt with custom text override"""
    config = {
        "prefix": "D&D item: ",
        "suffix": ".",
        "include_category": False,
        "max_length": 1000
    }

    entity = {"name": "Sword", "description": "Normal sword"}

    builder = PromptBuilder(config, "items")
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

    config = {"include_category": False, "max_length": 1000}
    builder = PromptBuilder(config, "spells")

    flavor = builder._extract_flavor_text(entity)

    assert "You create three glowing darts" in flavor


def test_extract_category_nested_field():
    """Test extracting category from nested field"""
    entity = {
        "name": "Longsword",
        "item_type": {"name": "Weapon", "code": "W"}
    }

    config = {
        "include_category": True,
        "category_field": "item_type.name",
        "max_length": 1000
    }

    builder = PromptBuilder(config, "items")
    category = builder._extract_category(entity)

    assert category == "Weapon"
