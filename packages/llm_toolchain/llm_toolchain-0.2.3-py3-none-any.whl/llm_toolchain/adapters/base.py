# file: base.py (Corrected Final Version)

from abc import ABC, abstractmethod
from typing import Any, Callable, get_type_hints, Sequence, Union
import inspect

# These imports depend on your project structure
from ..core import Tool
from ..models import ParseResult

class BaseAdapter(ABC):
    """An abstract base class for creating model-specific LLM adapters.

    The primary role of an adapter is to provide a standardized interface for
    interacting with various LLM clients, which often have different method names
    and response structures.

    This class introduces a dynamic "discovery" mechanism. Instead of hardcoding
    method calls like `llm_client.chat.completions.create(...)`, the adapter
    traverses a list of potential attribute paths (strategies) to find the correct
    method for making an API call and the correct path for parsing a response.

    Once a valid path is found, it's cached for subsequent calls to improve
    performance. This makes the system resilient to minor SDK updates and flexible
    enough to support a wide range of clients.

    Attributes:
        system_prompt (str | None): An optional system prompt to be used by the adapter.
        _run_callable (Callable | None): Caches the discovered callable for making LLM calls.
        _parse_callable (Callable | None): Caches the discovered callable for parsing LLM responses.
    """
    def __init__(
        self,
        system_prompt: str | None = None,
        manual_run_path: Sequence[str] | None = None,
        manual_parse_path: Sequence[Union[str, int]] | None = None,
    ):
        """Initializes the BaseAdapter.

        Args:
            system_prompt: An optional default system prompt to prepend to messages.
            manual_run_path: An optional, explicit attribute path to the LLM client's
                run method (e.g., ['chat', 'completions', 'create']). This will
                bypass the automatic discovery process.
            manual_parse_path: An optional, explicit path to the parsable content
                within an LLM response object (e.g., ['choices', 0, 'message']).
                This bypasses automatic discovery.
        """
        self.system_prompt = system_prompt
        # Caching for discovered callables. Can be pre-populated by manual paths.
        self._run_callable: Callable | None = manual_run_path
        self._parse_callable: Callable | None = manual_parse_path

    # --- Abstract Methods for Subclass Implementation ---

    @abstractmethod
    def _get_run_strategies(self) -> list[Sequence[str]]:
        """Provides a list of possible attribute paths to the LLM's run method.

        Subclasses MUST implement this method to return a list of candidate paths.
        The discovery logic will try these paths in order.

        Example:
            return [
                ['chat', 'completions', 'create'],  # For OpenAI's client
                ['generate_content'],              # For Gemini's client
            ]

        Returns:
            A list of sequences, where each sequence is a path to a potential run method.
        """
        pass

    @abstractmethod
    def _get_parse_strategies(self) -> list[Sequence[Union[str, int]]]:
        """Provides a list of possible paths to the parseable content in a response.

        Subclasses MUST implement this method to return a list of candidate paths
        to the part of the LLM response that contains the tool calls or message.

        Example:
            return [
                ['choices', 0, 'message', 'tool_calls'], # For OpenAI tool calls
                ['choices', 0, 'message'],              # For OpenAI messages
            ]

        Returns:
            A list of sequences, where each sequence is a path of attributes and/or
            indices leading to the response content.
        """
        pass

    @abstractmethod
    def _build_request(self, messages: list[dict], tools: list[dict], **kwargs) -> dict:
        """Constructs the model-specific request payload.

        Subclasses MUST implement this method to translate a generic list of
        messages and tools into the specific dictionary format expected by the
        target LLM's API.

        Args:
            messages: A list of messages in a standardized format.
            tools: A list of tool schemas in the model-specific format.
            **kwargs: Additional keyword arguments for the API call (e.g., 'temperature').

        Returns:
            A dictionary representing the complete request payload for the LLM API.
        """
        pass

    @abstractmethod
    def generate_schema(self, tool: Tool) -> Any:
        """Generates the model-specific schema for a single tool.

        Subclasses MUST implement this method to convert a universal `Tool` object
        into the specific format required by the target LLM's tool-calling API.

        Args:
            tool: The generic `Tool` object to convert.

        Returns:
            The model-specific representation of the tool (e.g., a dictionary).
        """
        pass

    # --- Core Discovery and Helper Logic ---

    def _traverse_path(self, obj: Any, path: Sequence[Union[str, int]]) -> Any:
        """Accesses a nested value in an object using a sequence of keys/attributes.

        This helper function is central to the discovery mechanism, allowing the
        adapter to dynamically navigate through client objects and response data
        structures.

        Args:
            obj: The object to traverse (e.g., an LLM client or a response object).
            path: A sequence of attribute names (str) or list/tuple indices (int).

        Returns:
            The value found at the end of the path.
        """
        for key in path:
            # Use dictionary-style access for indices, attribute access for strings.
            obj = obj[key] if isinstance(key, int) else getattr(obj, key)
        return obj

    def _discover_run_callable_if_needed(self, llm_client: Any, test_payload: dict):
        """Finds and caches the correct method for running an LLM call.

        This method is called once per adapter instance. It iterates through the
        strategies provided by `_get_run_strategies` and attempts to call each
        one with a minimal, non-disruptive `test_payload`. The first path that
        results in a successful call is cached as the `_run_callable`.

        Args:
            llm_client: The LLM client instance.
            test_payload: A minimal, safe request dictionary to test callables.

        Raises:
            NotImplementedError: If no valid, callable run path can be found.
        """
        # If a callable is already cached or was manually provided, do nothing.
        if self._run_callable and isinstance(self._run_callable, Callable):
            return

        print("--- Discovering LLM run path... ---")
        # Use the manual path as the only strategy if it exists, otherwise get all strategies.
        strategies = [self._run_callable] if self._run_callable else self._get_run_strategies()

        for path in strategies:
            try:
                # Find the potential method by traversing the client object.
                method = self._traverse_path(llm_client, path)
                if callable(method):
                    # Test the method with a harmless payload to ensure it works.
                    method(**test_payload)
                    # If the test call succeeds, cache the method and exit.
                    self._run_callable = method
                    print(f"--- Run path discovered: client.{'.'.join(path)} ---")
                    return
            except (AttributeError, TypeError, IndexError, KeyError):
                # This path is invalid; try the next strategy.
                continue
        # If no strategies succeeded, the adapter cannot function.
        raise NotImplementedError("Could not discover a valid run path for the LLM client.")

    def _discover_parse_callable_if_needed(self, response: Any):
        """Finds and caches the correct path to the content in an LLM response.

        Similar to run path discovery, this method iterates through strategies from
        `_get_parse_strategies` to find a valid path to the relevant content within
        a response object. It does not need to execute a call, only verify existence.
        The found path is used to create a simple lambda function for parsing.

        Args:
            response: A sample response object from the LLM client.

        Raises:
            NotImplementedError: If no valid parse path can be found in the response.
        """
        # If a callable is already cached or was manually provided, do nothing.
        if self._parse_callable and isinstance(self._parse_callable, Callable):
            return

        print("--- Discovering LLM parse path... ---")
        strategies = [self._parse_callable] if self._parse_callable else self._get_parse_strategies()

        for path in strategies:
            try:
                # Attempt to traverse the response object to see if the path is valid.
                content = self._traverse_path(response, path)
                # If successful, create and cache a simple callable that extracts content.
                self._parse_callable = lambda resp: self._traverse_path(resp, path)
                print(f"--- Parse path discovered: response.{'.'.join(map(str, path))} ---")
                return
            except (AttributeError, TypeError, IndexError, KeyError):
                # This path is invalid; try the next strategy.
                continue
        # If no strategies succeeded, the adapter cannot parse responses.
        raise NotImplementedError("Could not discover a valid parse path for the response object.")

    # --- Public-Facing Orchestration Methods ---

    def chat(self, llm_client: Any, messages: list[dict], tools: list[dict], **kwargs) -> Any:
        """Orchestrates an LLM call from building the request to execution.

        This is the main entry point for making an LLM call. It ensures the run
        path is discovered (if necessary) before building the final request payload
        and executing the call.

        Args:
            llm_client: The LLM client instance to use for the call.
            messages: The list of messages for the conversation.
            tools: The list of model-specific tool schemas.
            **kwargs: Additional arguments for the LLM API call.

        Returns:
            The raw response object from the LLM client.
        """
        # Create a safe, minimal payload for the discovery test call.
        # This avoids using tools and limits token usage to prevent unnecessary cost.
        test_kwargs = kwargs.copy()
        test_kwargs.setdefault('max_tokens', 2)
        test_payload = self._build_request(messages, [], **test_kwargs)
        self._discover_run_callable_if_needed(llm_client, test_payload)

        # Build the actual, final request payload with all tools and arguments.
        request_payload = self._build_request(messages, tools, **kwargs)
        # Execute the call using the now-guaranteed-to-exist run callable.
        return self._run_callable(**request_payload)

    def parse(self, response: Any) -> Any:
        """Orchestrates the parsing of an LLM response.

        This is the main entry point for extracting content from a raw response.
        It ensures the parse path is discovered on the first run and then uses the
        cached parser to extract the relevant content.

        Args:
            response: The raw response object from the LLM client.

        Returns:
            The extracted content (e.g., a message object, tool calls).
        """
        # Discover and cache the parse logic on the first call.
        self._discover_parse_callable_if_needed(response)
        # Use the cached callable to extract the content.
        return self._parse_callable(response)

    # --- Tool Schema Generation ---

    def _inspect_and_build_json_schema(self, tool: Tool) -> dict:
        """Creates a generic JSON schema for a tool using Python's introspection.

        This is a universal helper method that does not depend on any specific LLM.
        It inspects a Tool's function signature and type hints to generate a
        standardized, dictionary-based representation of its parameters. This
        generic schema is then passed to the abstract `generate_schema` method for
        model-specific formatting.

        Args:
            tool: The Tool object to inspect.

        Returns:
            A dictionary representing the tool in a generic JSON Schema-like format.
        """
        # Retrieve type hints and function signature.
        type_hints = get_type_hints(tool.function)
        properties = {}
        required = []

        for name, param in tool.signature.parameters.items():
            # Infer the Python type from type hints, defaulting to 'str'.
            py_type = type_hints.get(name, str)

            # Map Python types to JSON Schema types.
            if py_type is str:
                properties[name] = {"type": "string"}
            elif py_type is int:
                properties[name] = {"type": "integer"}
            elif py_type is float:
                properties[name] = {"type": "number"}
            elif py_type is bool:
                properties[name] = {"type": "boolean"}
            else: # Default for complex types like lists, dicts, etc.
                properties[name] = {"type": "string"}

            # A parameter is required if it doesn't have a default value.
            if param.default is inspect.Parameter.empty:
                required.append(name)

        # Assemble the final schema structure.
        return {
            "name": tool.name,
            "description": tool.description,
            "parameters_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }