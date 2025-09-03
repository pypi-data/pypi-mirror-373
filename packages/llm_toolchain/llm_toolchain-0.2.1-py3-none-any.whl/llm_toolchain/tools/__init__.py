import pkgutil
import importlib
import inspect

from ..core import Tool

# --- Dynamic Tool Discovery ---

# This list will be populated automatically.
__all__ = []

# Get the current package name (e.g., 'toolchain.tools')
package_name = __name__
# Get the path to this package
package_path = __path__

# Iterate over all modules in this package directory
for _, module_name, _ in pkgutil.iter_modules(package_path):
    if module_name == "__init__":
        continue

    # Import each module dynamically
    module = importlib.import_module(f".{module_name}", package_name)

    # Inspect the module for functions decorated with @tool
    for name, obj in inspect.getmembers(module):
        # Our decorator wraps functions in the 'Tool' class
        if isinstance(obj, Tool):
            # Add the tool's name to __all__ so it can be imported with '*'
            __all__.append(name)
            # Make the tool available directly on the package
            # (e.g., so you can do 'from toolchain.tools import get_weather')
            globals()[name] = obj

