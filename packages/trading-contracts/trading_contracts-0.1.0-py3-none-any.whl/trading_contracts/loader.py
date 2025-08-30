"""
Schema loader and validator for trading platform events
"""

import json
import importlib.resources as res
from typing import Dict, Any
from jsonschema import validate, Draft202012Validator, ValidationError


def load_schema(name: str) -> Dict[str, Any]:
    """
    Load JSON schema by event name.
    
    Args:
        name: Event name in format "event.type@version" (e.g., "strategy.signal@v1")
    
    Returns:
        Dictionary containing the JSON schema
        
    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file is invalid JSON
    """
    # Convert "strategy.signal@v1" to "strategy.signal.v1.schema.json"
    # Split by @ and replace v with v.
    if "@v" in name:
        event_part, version_part = name.split("@v")
        base = f"{event_part}.v{version_part}.schema.json"
    else:
        base = name + ".schema.json"

    
    try:
        # Try to find schema in the package data
        schema_path = res.files("trading_contracts").joinpath("kafka").joinpath(base)
        if not schema_path.exists():
            # Fallback to relative path from package root
            schema_path = res.files("trading_contracts").joinpath("../kafka").joinpath(base)
        
        # If still not found, try to find in the current working directory
        if not schema_path.exists():
            import os
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            schema_path = os.path.join(current_dir, "kafka", base)
        
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema not found: {name} -> {base}")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON in schema {base}: {e}", e.doc, e.pos)


def validate_event(name: str, payload: Dict[str, Any]) -> None:
    """
    Validate event payload against its schema.
    
    Args:
        name: Event name in format "event.type@version"
        payload: Event data to validate
        
    Raises:
        ValidationError: If payload doesn't match schema
        FileNotFoundError: If schema file doesn't exist
    """
    schema = load_schema(name)
    try:
        Draft202012Validator(schema).validate(payload)
    except ValidationError as e:
        raise ValidationError(f"Validation failed for {name}: {e.message}", e)


def get_schema_names() -> list[str]:
    """
    Get list of available schema names.
    
    Returns:
        List of schema names in format "event.type@version"
    """
    names = []
    
    # Try to find schemas in package data first
    try:
        schema_dir = res.files("trading_contracts").joinpath("kafka")
        if schema_dir.exists():
            for file_path in schema_dir.iterdir():
                if file_path.suffix == ".json" and file_path.stem.endswith(".schema"):
                    # Convert "strategy.signal.v1.schema.json" to "strategy.signal@v1"
                    name = file_path.stem.replace(".schema", "")
                    parts = name.split(".")
                    if len(parts) >= 3:
                        event_type = ".".join(parts[:-1])
                        version = parts[-1]
                        names.append(f"{event_type}@v{version}")
    except FileNotFoundError:
        pass
    
    # Fallback to relative path
    if not names:
        try:
            schema_dir = res.files("trading_contracts").joinpath("../kafka")
            for file_path in schema_dir.iterdir():
                if file_path.suffix == ".json" and file_path.stem.endswith(".schema"):
                    name = file_path.stem.replace(".schema", "")
                    parts = name.split(".")
                    if len(parts) >= 3:
                        event_type = ".".join(parts[:-1])
                        version = parts[-1]
                        names.append(f"{event_type}@v{version}")
        except FileNotFoundError:
            pass
    
    # Final fallback to current working directory
    if not names:
        try:
            import os
            current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            schema_dir = os.path.join(current_dir, "kafka")
            if os.path.exists(schema_dir):
                for file_name in os.listdir(schema_dir):
                    if file_name.endswith(".schema.json"):
                        # Convert "strategy.signal.v1.schema.json" to "strategy.signal@v1"
                        name = file_name.replace(".schema.json", "")
                        # Split by last dot to separate version
                        if "." in name:
                            last_dot_index = name.rfind(".")
                            event_type = name[:last_dot_index]
                            version = name[last_dot_index + 1:]
                            # Remove 'v' prefix from version if present
                            if version.startswith("v"):
                                version = version[1:]
                            names.append(f"{event_type}@v{version}")
        except Exception:
            pass
    
    return sorted(names)
