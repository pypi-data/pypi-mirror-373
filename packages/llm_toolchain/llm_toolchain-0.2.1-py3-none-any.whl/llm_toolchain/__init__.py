__version__ = "0.1.0"
# file: toolchain/__init__.py

"""
A Modern, Extensible LLM Toolchain.
"""

# --- Promote core classes from core.py ---
from .core import Toolchain, Tool, tool

# --- Promote the selector(s) if they are a core part of the user experience ---
from .selectors.semantic import SemanticToolSelector

# --- Promote essential models from models.py ---
from .models import FinalAnswer, ToolCall, ToolCalls

# --- Promote the most common adapters for convenience ---
from .adapters import (
    BaseAdapter,
    OpenAIAdapter,
    GenAIAdapter,
    VertexAIAdapter,
    PromptAdapter
)

# You can also promote selectors if they are a core part of the user experience
# from .selectors import SemanticToolSelector


# Optional: Define __all__ to control what 'from toolchain import *' does
__all__ = [
    "Toolchain",
    "Tool",
    "tool",
    "FinalAnswer",
    "ToolCall",
    "ToolCalls",
    "BaseAdapter",
    "OpenAIAdapter",
    "GenAIAdapter",
    "VertexAIAdapter",
    "PromptAdapter",
    "SemanticToolSelector",
]