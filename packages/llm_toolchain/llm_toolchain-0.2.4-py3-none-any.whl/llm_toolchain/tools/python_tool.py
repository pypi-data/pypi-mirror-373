import io
import sys
from contextlib import redirect_stdout
from ..core import tool

@tool
def run_python_code(code: str):
    """
    Executes a given string of Python code and returns its output.
    Use this for any tasks that require running code, calculations,
    or complex logic. The code is executed in a restricted environment.

    Args:
        code: A string containing valid Python code to be executed.
    """
    if not isinstance(code, str):
        return {"error": "Code must be provided as a string."}

    # Use a string buffer to capture the output of print() statements
    buffer = io.StringIO()
    
    # Create a restricted local scope for the execution
    local_scope = {}

    try:
        # Redirect standard output to our buffer
        with redirect_stdout(buffer):
            # Execute the code in the restricted scope
            exec(code, {"__builtins__": {}}, local_scope)
        
        output = buffer.getvalue()
        if not output:
            # If there was no print output, try to get the value of the last expression
            # (This is a simplified approach)
            if local_scope:
                output = str(list(local_scope.values())[-1])

        return {"output": output or "Code executed successfully with no output."}
    
    except Exception as e:
        # If an error occurs during execution, return the error message
        error_message = f"Error executing code: {type(e).__name__}: {e}"
        return {"error": error_message, "output": buffer.getvalue()}

