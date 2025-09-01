"""YAML configuration file utilities.

This module provides functions for loading and working with YAML configuration files.
"""
import yaml
from typing import Any, Dict
from novus_pytils.files.core import file_exists, get_files_by_extension
from novus_pytils.globals import YAML_EXTS

# TODO remove redundant methods and update tests

def load_yaml(filepath : str) -> dict:
    """
    Load a yaml file and return the contents as a dictionary.

    Args:
        filepath (str): The path to the yaml file.

    Returns:
        dict: The contents of the yaml file as a dictionary.
    """

    if not file_exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)
    
def get_yaml_files(dir_path : str) -> list:
    """
    Get all yaml files in a directory.

    Args:
        dir_path (str): The path to the directory.

    Returns:
        list: A list of paths to yaml files in the directory.
    """
    return get_files_by_extension(dir_path, YAML_EXTS)

def load_config(filepath: str) -> Dict[str, Any]:
    """
    Load a configuration file and return the contents as a dictionary.

    Args:
        filepath (str): The path to the configuration file.

    Returns:
        Dict[str, Any]: The contents of the configuration file.
    """
    return load_yaml(filepath)

def save_config(config: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save a configuration dictionary to a YAML file.

    Args:
        config (Dict[str, Any]): The configuration to save.
        filepath (str): The path to save the configuration to.
        indent (int): Number of spaces for indentation.
    """
    with open(filepath, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=indent)

def get_config_value(config: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Get a value from a configuration dictionary using dot notation.

    Args:
        config (Dict[str, Any]): The configuration dictionary.
        key (str): The key to retrieve (supports dot notation like 'section.subsection.key').
        default (Any): The default value to return if the key is not found.

    Returns:
        Any: The value associated with the key, or the default value.
    """
    keys = key.split('.')
    value = config
    try:
        for k in keys:
            value = value[k]
        return value
    except (KeyError, TypeError):
        return default

def set_config_value(config: Dict[str, Any], key: str, value: Any) -> None:
    """
    Set a value in a configuration dictionary using dot notation.

    Args:
        config (Dict[str, Any]): The configuration dictionary to modify.
        key (str): The key to set (supports dot notation like 'section.subsection.key').
        value (Any): The value to set.
    """
    keys = key.split('.')
    current = config
    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]
    current[keys[-1]] = value

def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate a configuration dictionary against a schema.

    Args:
        config (Dict[str, Any]): The configuration to validate.
        schema (Dict[str, Any]): The schema to validate against.

    Returns:
        bool: True if the configuration is valid, False otherwise.
    """
    # Basic validation - check if required keys exist
    for key, value in schema.items():
        if isinstance(value, dict) and 'required' in value and value['required']:
            if key not in config:
                return False
        elif isinstance(value, dict) and key in config:
            if not validate_config(config[key], value):
                return False
    return True

def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.

    Args:
        *configs: Variable number of configuration dictionaries to merge.

    Returns:
        Dict[str, Any]: The merged configuration dictionary.
    """
    result = {}
    for config in configs:
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_configs(result[key], value)
            else:
                result[key] = value
    return result

