import os
import yaml
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file with environment variable substitution"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Failed to parse YAML configuration: {e}")

    # Substitute environment variables
    config = _substitute_env_vars(config)

    return config


def _substitute_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively substitute ${VAR_NAME} with environment variables"""
    if isinstance(config, dict):
        return {k: _substitute_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_substitute_env_vars(item) for item in config]
    elif isinstance(config, str) and config.startswith("${") and config.endswith("}"):
        var_name = config[2:-1]
        return os.getenv(var_name, config)
    else:
        return config


def get_prompt_config(config: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
    """Get prompt configuration for specific entity type, with fallback to default"""
    prompts = config.get("prompts", {})

    if entity_type in prompts:
        return prompts[entity_type]

    return prompts.get("default", {})
