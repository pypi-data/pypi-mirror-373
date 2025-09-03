# file: utils/schema_generator.py

import inspect
from typing import get_type_hints


def generate_schema(func: callable) -> dict:
    """Generates a JSON schema for a function's parameters using introspection.

    This utility inspects a Python function to automatically build a schema
    that describes its name, description (from the docstring), and parameters
    (including their names and inferred types).

    Note: This is a simplified implementation. It primarily handles basic Python
    types and does not cover more complex scenarios like default values, union
    types, or nested object schemas. The schema format is compatible with the
    OpenAI function-calling API.

    Args:
        func: The function to generate a schema for.

    Returns:
        A dictionary representing the JSON schema of the function.

    Raises:
        ValueError: If the function does not have a docstring.
    """
    if not func.__doc__:
        raise ValueError("Tool function must have a docstring for its description.")

    # Use the 'inspect' module to get the function's signature.
    sig = inspect.signature(func)
    # Use 'get_type_hints' to access the type annotations of the function.
    type_hints = get_type_hints(func)

    properties = {}
    required = []

    # Iterate over each parameter in the function's signature.
    for name, param in sig.parameters.items():
        # Get the parameter's type name (e.g., 'str', 'int') and convert to lowercase.
        # Default to 'str' if no type hint is provided.
        param_type = type_hints.get(name, str).__name__
        properties[name] = {"type": param_type.lower()}

        # If a parameter has no default value, it is considered required.
        if param.default is inspect.Parameter.empty:
            required.append(name)

    # Assemble the final schema in the format expected by OpenAI.
    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": inspect.getdoc(func),
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }