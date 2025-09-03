# file: adapters/openai.py

import json
from typing import Any, Sequence, Union

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer, ToolCalls


class OpenAIAdapter(BaseAdapter):
    """An adapter for OpenAI models (GPT-3.5, GPT-4, etc.).

    This class implements the specific logic for building requests and parsing
    responses for the OpenAI Chat Completions API.
    """

    def _get_run_strategies(self) -> list[Sequence[str]]:
        """Provides the standard attribute path to the OpenAI SDK's run method."""
        return [
            ("chat", "completions", "create")
        ]

    def _get_parse_strategies(self) -> list[Sequence[Union[str, int]]]:
        """Provides the path to the 'message' object in an OpenAI response."""
        return [
            ("choices", 0, "message")
        ]

    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Builds the request payload for the OpenAI Chat Completions API."""
        final_messages = []
        # Prepend the system prompt if it exists, as OpenAI handles it natively.
        if self.system_prompt:
            final_messages.append({"role": "system", "content": self.system_prompt})
        final_messages.extend(messages)

        payload = {
            "messages": final_messages,
            "model": "gpt-4o",  # A sensible default, can be overridden by kwargs.
        }
        # Allow users to pass in any other API parameters like 'temperature'.
        payload.update(kwargs)

        # The 'tools' parameter is a simple list of tool schemas.
        if tools:
            payload["tools"] = tools

        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """Parses the 'message' object from an OpenAI API response.

        The BaseAdapter provides the complete `message` object. This method then
        checks for either text content (a final answer) or a list of tool_calls.
        """
        message_object = super().parse(response)
        results: list[ParseResult] = []

        try:
            # Check for a standard text response.
            if message_object.content and isinstance(message_object.content, str):
                results.append(FinalAnswer(content=message_object.content.strip()))

            # Check for tool calls.
            if message_object.tool_calls:
                tool_calls_list = []
                for tc in message_object.tool_calls:
                    try:
                        # Arguments from the LLM are a JSON string and must be decoded.
                        arguments = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {"error": f"Malformed JSON from LLM: {tc.function.arguments}"}

                    tool_calls_list.append(
                        ToolCall(id=tc.id, name=tc.function.name, args=arguments)
                    )

                if tool_calls_list:
                    # Save the raw Pydantic model output for consistent history.
                    assistant_message = message_object.model_dump(exclude_unset=True)
                    results.append(ToolCalls(calls=tool_calls_list, assistant_message=assistant_message))

            return results
        except (AttributeError, IndexError) as e:
            return [FinalAnswer(content=f"Failed to parse OpenAI response: {e}")]

    def generate_schema(self, tool: Tool) -> dict:
        """Converts a generic Tool into the OpenAI-specific dictionary schema.

        OpenAI requires the schema to be wrapped in a specific structure:
        `{"type": "function", "function": {...}}`.
        """
        generic_schema = self._inspect_and_build_json_schema(tool)
        return {
            "type": "function",
            "function": {
                "name": generic_schema["name"],
                "description": generic_schema["description"],
                "parameters": generic_schema["parameters_schema"],
            },
        }