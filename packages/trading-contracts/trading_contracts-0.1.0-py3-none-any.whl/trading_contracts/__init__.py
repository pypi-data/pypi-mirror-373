"""
Trading Contracts - JSON Schema validation for trading platform events
"""

from .loader import load_schema, validate_event, get_schema_names

__version__ = "0.1.0"
__all__ = ["load_schema", "validate_event", "get_schema_names"]
