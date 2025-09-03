# file: toolchain/integrations/langchain.py

from langchain_core.tools import BaseTool
from ..core import Tool, tool
import inspect
from typing import Callable

def convert_langchain_tool(lc_tool: BaseTool) -> Tool:
    """Converts a LangChain BaseTool into our native Tool object."""

    # This is the function the LLM will ultimately call.
    def execution_func(*args, **kwargs):
        # LangChain tools often accept a single string or a dictionary of arguments.
        # We'll prioritize passing keyword arguments if they exist.
        if kwargs:
            return lc_tool.invoke(kwargs)
        # If no kwargs, pass the first positional argument.
        elif args:
            return lc_tool.invoke(args[0])
        else:
            return lc_tool.invoke({})

    # Reconstruct the function signature and docstring for our system.
    execution_func.__name__ = lc_tool.name
    execution_func.__doc__ = lc_tool.description

    # Create a new signature based on the LangChain tool's Pydantic schema.
    params = []
    if lc_tool.args_schema:
        for name, field in lc_tool.args_schema.model_fields.items():
            # Get type annotation, default to 'str' if not available
            annotation = field.annotation or str
            params.append(
                inspect.Parameter(
                    name,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=annotation
                )
            )
    execution_func.__signature__ = inspect.Signature(params)

    # Wrap the dynamically created function in our Tool class.
    # Note: We create a Tool directly, not using the @tool decorator here.
    return Tool(function=execution_func)




def convert_langchain_tools(lc_tools: list[BaseTool]) -> list[Tool]:
    """
    A convenience function to convert a list of LangChain tools
    into a list of native Toolchain Tools.
    """
    return [convert_langchain_tool(tool) for tool in lc_tools]