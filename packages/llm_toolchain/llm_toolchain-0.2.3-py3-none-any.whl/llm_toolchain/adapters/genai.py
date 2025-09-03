# file: adapters/genai.py

from ..utils.formatting import _keys_to_snake_case
import json
from typing import Any, Sequence, Union
from google.protobuf.json_format import MessageToDict

# Attempt to import the required library and provide a helpful error message
# if it's not installed.
try:
    from google.generativeai import types
except ImportError:
    raise ImportError(
        "To use the GenAIAdapter, please install the required library: "
        "'pip install google-generativeai'"
    )

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer, ToolCalls


class GenAIAdapter(BaseAdapter):
    """An adapter for Google Gemini models using the 'google-generativeai' library.

    This class implements the specific logic required to format requests for,
    and parse responses from, the Gemini API provided by this specific SDK.
    """

    def _get_run_strategies(self) -> list[Sequence[str]]:
        """Provides the specific attribute path to the Gemini SDK's run method."""
        return [
            ("generate_content",)
        ]

    def _get_parse_strategies(self) -> list[Sequence[Union[str, int]]]:
        """Provides the path to the parsable 'parts' list in a Gemini response."""
        return [
            ("candidates", 0, "content", "parts")
        ]

    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Builds the request payload for the Gemini 'generate_content' API.

        This method handles Gemini-specific formatting, such as renaming 'max_tokens'
        to 'max_output_tokens' and, crucially, wrapping the list of tool schemas
        into a single `types.Tool` object as required by the SDK.
        """
        contents = self._format_contents(messages)

        # Translate the generic 'max_tokens' argument to the Gemini-specific one.
        generation_config = kwargs.copy()
        if 'max_tokens' in generation_config:
            generation_config['max_output_tokens'] = generation_config.pop('max_tokens')

        payload = {
            "contents": contents,
            "generation_config": generation_config,
        }

        # The 'tools' parameter must be a list containing a single `types.Tool` object.
        # This object, in turn, contains the list of function declarations.
        if tools:
            gemini_tools = types.Tool(function_declarations=tools)
            payload["tools"] = [gemini_tools]

        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """Parses the 'parts' list from a Gemini response.

        The BaseAdapter's `parse` method has already extracted the `parts` list
        for us. This method iterates through that list, distinguishing between
        text content (`part.text`) and tool calls (`part.function_call`).

        A `FinalAnswer` is only returned if the model provides text AND does not
        make any tool calls.
        """
        all_parts = super().parse(response)
        results: list[ParseResult] = []

        try:
            tool_calls_list = []
            reasoning_text_parts = []
            has_tool_call = False

            for part in all_parts:
                # Aggregate any text parts from the model's response.
                if hasattr(part, 'text') and part.text:
                    reasoning_text_parts.append(part.text.strip())

                # Aggregate any tool calls from the model's response.
                if hasattr(part, 'function_call') and part.function_call:
                    has_tool_call = True
                    fc = part.function_call
                    # The arguments are already a dict-like object.
                    arguments = dict(fc.args)
                    tool_call_id = f"call_{fc.name}_{len(tool_calls_list)}"
                    tool_calls_list.append(
                        ToolCall(id=tool_call_id, name=fc.name, args=arguments)
                    )

            # Only treat text as a final answer if NO tool calls were made.
            if reasoning_text_parts and not has_tool_call:
                full_reasoning = "\n".join(reasoning_text_parts)
                results.append(FinalAnswer(content=full_reasoning))

            # If tool calls exist, package them up.
            if tool_calls_list:
                # Serialize the raw protobuf response to a dict for consistent
                # history management. This captures the exact model output.
                proto_dict = MessageToDict(response.candidates[0].content._pb)
                assistant_message = _keys_to_snake_case(proto_dict)

                results.append(ToolCalls(
                    calls=tool_calls_list,
                    assistant_message=assistant_message
                ))

            return results
        except (AttributeError, IndexError, TypeError, Exception) as e:
            # Fallback to returning an error message as the final answer.
            return [FinalAnswer(content=f"Failed to parse Gemini response: {e}")]

    def generate_schema(self, tool: Tool) -> dict:
        """Converts a generic Tool into the Gemini-specific dictionary schema."""
        generic_schema = self._inspect_and_build_json_schema(tool)
        # The Gemini API expects the parameter schema under the key 'parameters'.
        return {
            "name": generic_schema["name"],
            "description": generic_schema["description"],
            "parameters": generic_schema["parameters_schema"],
        }

    def _format_contents(self, messages: list[dict]) -> list[dict]:
        """Converts the standardized message history into Gemini's 'contents' format."""
        contents = []
        # Gemini doesn't have a dedicated system prompt, so we emulate it with a
        # user/model turn at the beginning of the conversation.
        if self.system_prompt:
            contents.append({"role": "user", "parts": [{"text": self.system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})

        for msg in messages:
            # The API uses 'model' for the assistant's role.
            role = "model" if msg.get("role") == "assistant" else msg.get("role")

            if not role:
                continue

            if role == "tool":
                # Format the tool result into a 'function_response' part.
                part = {
                    "function_response": {
                        "name": msg.get("name"),
                        "response": json.loads(msg.get("content", '""'))
                    }
                }
                contents.append({"role": "tool", "parts": [part]})
            elif role == "model" and "parts" in msg:
                # This handles re-inserting the raw assistant message from history.
                contents.append(msg)
            else:
                # Format a standard user or model message.
                part = {"text": msg.get("content", "")}
                contents.append({"role": role, "parts": [part]})

        return contents