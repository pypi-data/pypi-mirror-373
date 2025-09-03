import json
from typing import Callable
import inspect
from .models import FinalAnswer, ParseResult, ToolCall, ToolCalls

# --- The Tool Class and Decorator ---
# No changes are needed for the Tool class or the @tool decorator
class Tool:
    """A simpler wrapper that just holds the function and its signature."""
    def __init__(self, function: Callable):
        self.name = function.__name__
        self.description = inspect.getdoc(function)
        self.signature = inspect.signature(function)
        self.function = function

def tool(func: Callable) -> Tool:
    """The decorator now just wraps the function in the Tool class."""
    if not func.__doc__:
        raise ValueError("Tool function must have a docstring for its description.")
    return Tool(function=func)

# --- The Main Toolchain Class ---

class Toolchain:
    """
    The main orchestrator that manages tools and executes LLM-driven workflows.
    """

    def __init__(self, tools: list[Tool], llm_client: any, adapter: any = None, selector: any = None):
        """
        Initializes the Toolchain with a list of tools and an LLM client.

        Args:
            tools: A list of all available Tool objects.
            llm_client: An instantiated LLM client (e.g., OpenAI(), genai.GenerativeModel(...)).
            adapter: An optional pre-configured adapter.
            selector: An optional tool selector instance (e.g., SemanticToolSelector).
        """
        # Store all available tools in a dictionary for easy lookup by name
        self.all_tools: dict[str, Tool] = {t.name: t for t in tools}

        self.llm_client = llm_client
        self.selector = selector
        self.adapter = adapter or self._get_adapter(llm_client)

    def _get_adapter(self, llm_client):
        # ... (no changes to this method) ...
        from .adapters import OpenAIAdapter
        if isinstance(llm_client, OpenAI):
            return OpenAIAdapter()
        if isinstance(llm_client, genai.GenerativeModel):
            from .adapters import GeminiAdapter
            return GeminiAdapter()
        from .adapters import PromptAdapter
        return PromptAdapter()

    # --- High-Level "Simple" Method ---

    def run(self, prompt: str, messages: list[dict] = None, **llm_params) -> str:
        """
        The main high-level method. Handles the entire ReAct loop automatically.
        
        Args:
            prompt: The user's prompt for this turn.
            messages: The existing conversation history, if any.
            tools: An optional list of tool names the user wants to make available for this turn.
            **llm_params: Additional keyword arguments to pass to the LLM.
        """
        messages = messages or []
        messages.append({"role": "user", "content": prompt})

        while True:
            # --- Start of the Tool Selection Logic ---
            
            # 1. Start with the tools explicitly provided by the user
            user_selected_tools = set((list(self.all_tools.values())) or [])
            available_tools_for_turn: dict[str, Tool] = self.all_tools.copy()
            # 2. If a selector is configured, get its suggestions
            selector_selected_tools = set()
            if self.selector:
                # Use the last user message for semantic context
                last_user_message = next((m['content'] for m in reversed(messages) if m.get('role') == 'user' and 'content' in m), None)
                if last_user_message:
                    selector_selected_tools = self.selector.select_tools(prompt=last_user_message)
                    for t in selector_selected_tools:
                        available_tools_for_turn[t.name] = t


            

            # 5. Generate schemas for ONLY the relevant tools
            tools_as_schema = [self.adapter.generate_schema(t) for t in selector_selected_tools.union(user_selected_tools)]

            # --- End of the Tool Selection Logic ---
            print("Hello")
            print(messages)
            response = self.adapter.chat(
                llm_client=self.llm_client,
                messages=messages,
                tools=tools_as_schema, # Pass the dynamically selected tools
                **llm_params
            )
            
            parsed_results = self.adapter.parse(response)

            final_answers = [r for r in parsed_results if isinstance(r, FinalAnswer)]
            # The list now contains ToolCalls objects, not tuples
            tool_calls_results = [r for r in parsed_results if isinstance(r, ToolCalls)]

            if tool_calls_results:
                if final_answers:
                    full_text = "\n".join([answer.content for answer in final_answers])
                    print(f"LLM Message: {full_text}")

                tool_outputs = []
                # Iterate through the ToolCalls objects
                for result in tool_calls_results:
                    # Access attributes by name, not by unpacking a tuple
                    messages.append(result.assistant_message)
                    for tool_call in result.calls:
                        output = self.execute_tool(tool_call, available_tools_for_turn)
                        tool_outputs.append(output)
                
                messages.extend(tool_outputs)
                continue

            if final_answers:
                return "\n".join([answer.content for answer in final_answers])

    # --- Low-Level "Tinkering" Building Blocks ---
    
    def execute_tool(self, tool_call: ToolCall, available_tools_for_turn: dict) -> dict:
        print(f"Executing tool: {tool_call.name} with args: {tool_call.args}")
        """Executes a single tool call and returns the formatted output."""
        # Check against the full list of all available tools
        if tool_call.name not in available_tools_for_turn:
            return {"error": f"Tool '{tool_call.name}' not found."}

        try:
            tool_obj = available_tools_for_turn[tool_call.name]
            output = tool_obj.function(**tool_call.args)
            # Gemini's native function calling expects the 'response' part of a
            # function_response to be a JSON object (dict). If the tool returns
            # a raw string or other primitive, we wrap it in a dict.
            if not isinstance(output, dict):
                output = {"result": output}

            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": json.dumps(output),
            }
        except Exception as e:
            error_output = {"error": f"Error executing tool: {e}"}
            return {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": json.dumps(error_output),
            }
