# file: adapters/prompt.py

import json
import re
from typing import Any, Sequence, Union

from .base import BaseAdapter
from ..core import Tool
from ..models import ParseResult, ToolCall, FinalAnswer, ToolCalls


class PromptAdapter(BaseAdapter):
    """An adapter for LLMs without native tool-calling APIs.

    This adapter works by "prompting" the model to use tools. It injects a
    detailed set of instructions into the system prompt, including string-based
    schemas for each tool. It then uses regular expressions to parse a JSON
    object containing tool calls from the model's plain text response.

    It includes many discovery strategies to maximize compatibility with various
    LLM SDKs (OpenAI, Anthropic, Gemini, etc.).
    """

    def _get_run_strategies(self) -> list[Sequence[str]]:
        """Provides a broad list of common run paths for maximum compatibility."""
        return [
            ("chat", "completions", "create"),  # OpenAI, etc.
            ("messages", "create"),            # Anthropic
            ("generate_content",)             # Gemini
        ]

    def _get_parse_strategies(self) -> list[Sequence[Union[str, int]]]:
        """Provides a broad list of common text content paths."""
        return [
            ("choices", 0, "message", "content"), # OpenAI
            ("content", 0, "text"),               # Anthropic
            ("text",)                             # Simple text responses
        ]

    def _build_request(self, messages: list[dict], tools: list[str], **kwargs) -> dict:
        """Builds a request by injecting tool definitions into the system prompt."""
        # This detailed instruction prompt tells the model how to behave and
        # what format to use for tool calls.
        instruction_prompt = f"""
You are a helpful assistant with access to a set of tools.
## AVAILABLE TOOLS:
{"\n".join(tools)}
## RESPONSE INSTRUCTIONS:
When you decide to call one or more tools, you MUST respond with ONLY a single, valid JSON object. Your entire response must be the JSON object. The JSON object must conform to this exact schema: {{"tool_calls": [{{"tool_name": "<tool_name>", "arguments": {{"<arg_name": "<arg_value>"}}}}]}}
If you do not need to call any tools, provide a final, natural language answer to the user.
"""
        # Prepend the detailed instructions to the message history.
        final_messages = [{"role": "system", "content": instruction_prompt}]
        final_messages.extend(messages)

        # Prepare a simple 'contents' structure for Gemini-like APIs.
        contents = []
        for msg in final_messages:
            role = "model" if msg.get("role") in ["assistant", "system"] else "user"
            contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})

        # The payload includes both 'messages' and 'contents' to work with
        # both OpenAI-style and Gemini-style APIs.
        payload = {
            "messages": final_messages,
            "contents": contents,
        }
        payload.update(kwargs)

        return payload

    def parse(self, response: Any) -> list[ParseResult]:
        """Parses the raw text response to find a JSON object with tool calls."""
        response_text = super().parse(response)

        if not response_text or not isinstance(response_text, str):
            return [FinalAnswer(content=str(response_text))]

        # Default to assuming the whole response is a final answer.
        results: list[ParseResult] = [FinalAnswer(content=response_text)]

        # Use regex to find a JSON block anywhere in the model's text output.
        match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if match:
            json_string = match.group(0)
            try:
                # If a JSON block is found, attempt to parse it for tool calls.
                parsed_json = json.loads(json_string)
                tool_calls_data = parsed_json.get("tool_calls")
                if isinstance(tool_calls_data, list):
                    tool_calls_list = []
                    for call_data in tool_calls_data:
                        tool_name = call_data.get("tool_name")
                        arguments = call_data.get("arguments")
                        if isinstance(tool_name, str) and isinstance(arguments, dict):
                            tool_call_id = f"call_{tool_name}_{len(tool_calls_list)}"
                            tool_calls_list.append(ToolCall(id=tool_call_id, name=tool_name, args=arguments))

                    # If valid tool calls were parsed, add them to the results.
                    if tool_calls_list:
                        # The raw JSON string is the assistant's message for history.
                        assistant_message = {"role": "assistant", "content": json_string}
                        results.append(ToolCalls(calls=tool_calls_list, assistant_message=assistant_message))
            except json.JSONDecodeError:
                # If JSON parsing fails, do nothing and just return the final answer.
                pass

        return results

    def generate_schema(self, tool: Tool) -> str:
        """Generates a human-readable string representation of the tool.

        Instead of a JSON object, this schema is a simple string that clearly
        describes the tool's signature and purpose for the LLM to read.
        Example: "- get_weather(location: string): Gets the current weather."
        """
        generic_schema = self._inspect_and_build_json_schema(tool)
        params = [f'{name}: {schema.get("type", "any")}' for name, schema in generic_schema["parameters_schema"]["properties"].items()]
        param_str = ", ".join(params)
        return f"- {generic_schema['name']}({param_str}): {generic_schema['description']}"