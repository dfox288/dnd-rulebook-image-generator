import os
import pytest
from src.config import load_config, get_prompt_config


def test_load_config_reads_yaml():
    """Test that config loads successfully"""
    config = load_config()
    assert config is not None
    assert "api" in config
    assert "openai" in config
    assert "prompts" in config


def test_get_prompt_config_returns_entity_specific():
    """Test that entity-specific prompts are returned"""
    config = load_config()
    spell_prompts = get_prompt_config(config, "spells")

    assert spell_prompts["include_category"] is True
    assert "{category}" in spell_prompts["prefix"]
    assert spell_prompts["category_field"] == "school.name"


def test_get_prompt_config_falls_back_to_default():
    """Test that unknown entity types fall back to default"""
    config = load_config()
    unknown_prompts = get_prompt_config(config, "unknown_type")

    assert unknown_prompts["include_category"] is False
    assert "Fantasy art in D&D style" in unknown_prompts["prefix"]


def test_openai_api_key_from_env():
    """Test that API key is loaded from environment"""
    os.environ["OPENAI_API_KEY"] = "test_key_123"
    config = load_config()

    assert config["openai"]["api_key"] == "test_key_123"
