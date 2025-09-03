"""This module provides utility functions for formatting data."""
import re
from typing import Any

def _keys_to_snake_case(d: Any) -> Any:
    """
    Recursively converts dictionary keys from camelCase to snake_case.

    Args:
        d: The dictionary or list to convert.

    Returns:
        The converted dictionary or list.
    """
    if isinstance(d, dict):
        return {
            re.sub(r'(?<!^)(?=[A-Z])', '_', k).lower(): _keys_to_snake_case(v)
            for k, v in d.items()
        }
    if isinstance(d, list):
        return [_keys_to_snake_case(i) for i in d]
    return d