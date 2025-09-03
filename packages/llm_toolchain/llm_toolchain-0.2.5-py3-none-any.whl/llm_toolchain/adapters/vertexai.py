# file: adapters/vertexai.py

import json
from typing import Any, Sequence, Union

# Attempt to import the required library and provide a helpful error message.
try:
    from vertexai.generative_models import Tool as VertexTool
    from vertexai.generative_models import FunctionDeclaration
except ImportError:
    raise ImportError(
        "To use the VertexAIAdapter, please install the required library: "
        "'pip install google-cloud-aiplatform'"
    )

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer, ToolCalls


class VertexAIAdapter(BaseAdapter):
    """An adapter for Google Gemini models via the Vertex AI SDK.

    This adapter uses the 'google-cloud-aiplatform' library, which has a
    slightly different API and request/response structure compared to the
    'google-generativeai' library.
    """

    def _get_run_strategies(self) -> list[Sequence[str]]:
        """Provides the specific attribute path to the Vertex AI SDK's run method."""
        return [
            ("generate_content",)
        ]

    def _get_parse_strategies(self) -> list[Sequence[Union[str, int]]]:
        """Provides the path to the parsable 'parts' list in a Vertex AI response."""
        return [
            ("candidates", 0, "content", "parts")
        ]

    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Builds the request payload for the Vertex AI 'generate_content' API.

        This method handles Vertex AI-specific tool formatting. Each tool schema
        must be converted into a `FunctionDeclaration` object, and the list of
        these declarations must then be wrapped in a `VertexTool` object.
        """
        contents = self._format_contents(messages)

        generation_config = kwargs.copy()
        if 'max_tokens' in generation_config:
            generation_config['max_output_tokens'] = generation_config.pop('max_tokens')

        payload = {
            "contents": contents,
            "generation_config": generation_config,
        }

        if tools:
            # Step 1: Convert each tool schema dict into a FunctionDeclaration object.
            func_declarations = [
                FunctionDeclaration(**tool_schema) for tool_schema in tools
            ]
            # Step 2: Wrap the list of declarations in a VertexTool object.
            # The API expects a list containing one or more of these Tool objects.
            vertex_tools = [VertexTool(function_declarations=func_declarations)]
            payload["tools"] = vertex_tools

        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """Parses the 'parts' list from a Vertex AI response."""
        all_parts = super().parse(response)
        results: list[ParseResult] = []

        try:
            tool_calls_list = []
            reasoning_text_parts = []
            has_tool_call = False

            for part in all_parts:
                if hasattr(part, 'text') and part.text:
                    reasoning_text_parts.append(part.text.strip())

                if hasattr(part, 'function_call') and part.function_call:
                    has_tool_call = True
                    fc = part.function_call
                    arguments = dict(fc.args)
                    tool_call_id = f"call_{fc.name}_{len(tool_calls_list)}"
                    tool_calls_list.append(
                        ToolCall(id=tool_call_id, name=fc.name, args=arguments)
                    )

            if reasoning_text_parts and not has_tool_call:
                full_reasoning = "\n".join(reasoning_text_parts)
                results.append(FinalAnswer(content=full_reasoning))

            if tool_calls_list:
                # For history, serialize the response part using the SDK's to_dict() method.
                assistant_message = response.candidates[0].content.to_dict()
                results.append(ToolCalls(
                    calls=tool_calls_list,
                    assistant_message=assistant_message
                ))

            return results
        except (AttributeError, IndexError, TypeError, Exception) as e:
            return [FinalAnswer(content=f"Failed to parse Gemini response: {e}")]

    def generate_schema(self, tool: Tool) -> dict:
        """Converts a generic Tool into the schema for Vertex AI FunctionDeclarations."""
        generic_schema = self._inspect_and_build_json_schema(tool)
        return {
            "name": generic_schema["name"],
            "description": generic_schema["description"],
            "parameters": generic_schema["parameters_schema"],
        }

    def _format_contents(self, messages: list[dict]) -> list[dict]:
        """Formats the message history into the Vertex AI 'contents' format."""
        contents = []
        if self.system_prompt:
            contents.append({"role": "user", "parts": [{"text": self.system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})

        for msg in messages:
            role = "model" if msg.get("role") == "assistant" else msg.get("role")

            if not role:
                continue

            # CRITICAL: Unlike other APIs, Vertex AI requires that the response
            # from a tool call be sent back with the 'user' role, not the 'tool' role.
            if role == "tool":
                part = {
                    "function_response": {
                        "name": msg.get("name"),
                        # The response content must also be wrapped in a dict.
                        "response": {"content": msg.get("content", "")}
                    }
                }
                contents.append({"role": "user", "parts": [part]})
            elif role == "model" and "parts" in msg:
                # Re-insert the raw assistant message from history.
                contents.append(msg)
            else:
                part = {"text": msg.get("content", "")}
                contents.append({"role": role, "parts": [part]})

        return contents