"""
This module provides a function to load configuration from a YAML file.
"""

import yaml


def load_config(path: str = "config/config.yaml") -> dict:
    """
    Load configuration from a YAML file.
    Args:
        path: Path to the YAML configuration file.

    Returns:
        Parsed configuration data.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            if config is None:
                raise ValueError("Configuration file is empty or invalid")
            return config
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Configuration file {path} not found {exc}") from exc
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file '{path}': {e}") from e
