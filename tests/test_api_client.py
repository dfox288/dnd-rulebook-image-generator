import pytest
import responses
from src.generator.api_client import DndApiClient, LOOKUP_ENTITY_TYPES


@responses.activate
def test_fetch_entities_paginated():
    """Test fetching entities with pagination"""
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/spells",
        json={
            "data": [
                {"id": 1, "slug": "fireball", "name": "Fireball", "description": "A blast of fire"},
                {"id": 2, "slug": "magic-missile", "name": "Magic Missile", "description": "Magical darts"}
            ],
            "meta": {"current_page": 1, "last_page": 1}
        },
        status=200
    )

    client = DndApiClient(base_url="http://localhost:8080/api/v1", timeout=30)
    entities = list(client.fetch_entities("spells"))

    assert len(entities) == 2
    assert entities[0]["slug"] == "fireball"
    assert entities[1]["slug"] == "magic-missile"


@responses.activate
def test_fetch_entities_multiple_pages():
    """Test pagination across multiple pages"""
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/items",
        json={
            "data": [{"id": 1, "slug": "longsword", "name": "Longsword"}],
            "meta": {"current_page": 1, "last_page": 2}
        },
        status=200
    )
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/items",
        json={
            "data": [{"id": 2, "slug": "shield", "name": "Shield"}],
            "meta": {"current_page": 2, "last_page": 2}
        },
        status=200
    )

    client = DndApiClient(base_url="http://localhost:8080/api/v1", timeout=30)
    entities = list(client.fetch_entities("items"))

    assert len(entities) == 2


@responses.activate
def test_fetch_entities_with_limit():
    """Test limiting number of entities fetched"""
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/spells",
        json={
            "data": [
                {"id": i, "slug": f"spell-{i}", "name": f"Spell {i}"}
                for i in range(1, 11)
            ],
            "meta": {"current_page": 1, "last_page": 10}
        },
        status=200
    )

    client = DndApiClient(base_url="http://localhost:8080/api/v1", timeout=30)
    entities = list(client.fetch_entities("spells", limit=5))

    assert len(entities) == 5


@responses.activate
def test_fetch_lookup_entities_uses_lookups_prefix():
    """Test that lookup entity types use the /lookups/ prefix"""
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/lookups/sources",
        json={
            "data": [
                {"id": 1, "code": "PHB", "name": "Player's Handbook", "description": "Core rulebook"}
            ],
            "meta": {"current_page": 1, "last_page": 1}
        },
        status=200
    )

    client = DndApiClient(base_url="http://localhost:8080/api/v1", timeout=30)
    entities = list(client.fetch_entities("sources"))

    assert len(entities) == 1
    assert entities[0]["code"] == "PHB"


@responses.activate
def test_fetch_spell_schools_uses_lookups_prefix():
    """Test that spell-schools uses the /lookups/ prefix"""
    responses.add(
        responses.GET,
        "http://localhost:8080/api/v1/lookups/spell-schools",
        json={
            "data": [
                {"id": 1, "slug": "evocation", "name": "Evocation"}
            ],
            "meta": {"current_page": 1, "last_page": 1}
        },
        status=200
    )

    client = DndApiClient(base_url="http://localhost:8080/api/v1", timeout=30)
    entities = list(client.fetch_entities("spell-schools"))

    assert len(entities) == 1
    assert entities[0]["slug"] == "evocation"


def test_lookup_entity_types_constant():
    """Test that LOOKUP_ENTITY_TYPES contains expected values"""
    expected = {
        'sources', 'spell-schools', 'damage-types', 'sizes',
        'ability-scores', 'skills', 'item-types', 'item-properties',
        'conditions', 'proficiency-types', 'languages'
    }
    assert LOOKUP_ENTITY_TYPES == expected
