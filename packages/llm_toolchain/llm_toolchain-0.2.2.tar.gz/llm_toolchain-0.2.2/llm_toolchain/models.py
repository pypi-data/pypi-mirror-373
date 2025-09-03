from dataclasses import dataclass
from typing import Union, Any


@dataclass
class ToolCall:
    """A data class representing a tool call requested by the LLM."""

    id: str
    name: str
    args: dict


@dataclass
class FinalAnswer:
    """A data class representing a final answer from the LLM."""

    content: str


@dataclass
class ToolCalls:
    """A data container for one or more tool calls and the raw assistant message."""
    calls: list[ToolCall]
    assistant_message: dict[str, Any]

# A type hint for the result of parsing an LLM response
ParseResult = Union[list[ToolCall], FinalAnswer]
