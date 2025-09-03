import os
from pathlib import Path
from ..core import tool

# --- Configuration: All paths are now relative to the current working directory ---
CURRENT_WORKING_DIR = Path.cwd()

def _resolve_safe_path(filename: str) -> Path | None:
    """
    Resolves a filename to an absolute path, ensuring it's safely within
    the current working directory or one of its subdirectories.
    This prevents directory traversal attacks (e.g., using '../..').
    """
    # Create the path object relative to the CWD
    file_path = (CURRENT_WORKING_DIR / filename).resolve()
    
    # Check if the resolved path is a child of or the same as the CWD
    if CURRENT_WORKING_DIR in file_path.parents or file_path == CURRENT_WORKING_DIR:
        return file_path
    
    # Check for the edge case where the filename is just "."
    if filename.strip() == ".":
        return CURRENT_WORKING_DIR

    return None

@tool
def change_directory(directory: str):
    """
    Changes the current working directory for all subsequent file operations.

    Args:
        directory (str): The path to the new directory (e.g., 'new_folder' or '../').
    """
    global CURRENT_WORKING_DIR
    
    # First, resolve the path safely to prevent escaping the project root
    new_path_resolved = _resolve_safe_path(directory)
    
    if not new_path_resolved:
        return {"error": "Access denied. Cannot change to a directory outside of the project root."}

    if not new_path_resolved.is_dir():
        return {"error": f"Directory not found: '{directory}'"}
    
    # If it's safe, update the global CWD variable
    CURRENT_WORKING_DIR = new_path_resolved
    return {"status": "success", "new_directory": str(CURRENT_WORKING_DIR)}


@tool
def show_directory_tree(directory: str = "."):
    """
    Displays the entire directory structure starting from a given directory
    in a visual tree-like format.

    Args:
        directory (str, optional): The starting directory. Defaults to the current one.
    """
    start_path = _resolve_safe_path(directory)
    if not start_path or not start_path.is_dir():
        return {"error": f"Access denied or directory not found: '{directory}'"}

    tree_lines = [str(start_path.name)]
    
    def _build_tree(current_path: Path, prefix: str):
        """A recursive helper function to build the tree structure."""
        items = sorted(list(current_path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
        
        for i, item in enumerate(items):
            is_last = i == (len(items) - 1)
            connector = "└── " if is_last else "├── "
            tree_lines.append(f"{prefix}{connector}{item.name}")
            
            if item.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                _build_tree(item, new_prefix)

    try:
        _build_tree(start_path, "")
        return {"directory_tree": "\n".join(tree_lines)}
    except Exception as e:
        return {"error": f"Failed to generate directory tree: {e}"}
@tool
def list_files(directory: str = "."):
    """
    Lists all files and subdirectories within a specified directory,
    indicating whether each is a 'file' or a 'folder'.

    Do not use this tool to explore deeply nested structures, or 

    to find a specific file or explore deeply, consider using the 'show_directory_tree' tool instead.

    Args:
        directory (str, optional): The subdirectory to list. Defaults to the current directory.
    """
    safe_dir_path = _resolve_safe_path(directory)
    if not safe_dir_path or not safe_dir_path.is_dir():
        return {"error": f"Access denied or directory not found: '{directory}'"}
    
    try:
        items = []
        for item in safe_dir_path.iterdir():
            item_type = "folder" if item.is_dir() else "file"
            items.append({"name": item.name, "type": item_type})

        if not items:
            return {"contents": [], "message": f"The directory '{directory}' is empty."}
        
        # Sort the list to show folders first, then files, both alphabetically
        items.sort(key=lambda x: (x['type'], x['name']))

        return {"directory": str(safe_dir_path), "contents": items}
    except Exception as e:
        return {"error": f"Failed to list files: {e}"}
@tool
def read_file(filename: str):
    """
    Reads the entire content of a specified file.

    Args:
        filename: The path to the file (e.g., 'my_file.txt' or 'subdir/my_file.txt').
    """
    safe_path = _resolve_safe_path(filename)
    if not safe_path:
        return {"error": "Access denied. Cannot read outside of the current working directory."}
    
    if not safe_path.is_file():
        return {"error": f"File not found: '{filename}'"}
        
    try:
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"filename": filename, "content": content}
    except Exception as e:
        return {"error": f"Failed to read file: {e}"}

@tool
def write_file(filename: str, content: str):
    """
    Writes or overwrites a file with the given content.

    Args:
        filename: The path to the file (e.g., 'output.txt' or 'project/notes.md').
        content: The text content to write into the file.
    """
    safe_path = _resolve_safe_path(filename)
    if not safe_path:
        return {"error": "Access denied. Cannot write outside of the current working directory."}
    
    try:
        # Ensure the parent directory exists
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"File '{filename}' written successfully."}
    except Exception as e:
        return {"error": f"Failed to write file: {e}"}

@tool
def append_to_file(filename: str, content: str):
    """
    Appends content to the end of an existing file.

    Args:
        filename: The path to the file.
        content: The text content to append to the file.
    """
    safe_path = _resolve_safe_path(filename)
    if not safe_path:
        return {"error": "Access denied. Cannot write outside of the current working directory."}
    
    if not safe_path.is_file():
        return {"error": f"File not found: '{filename}'"}
        
    try:
        with open(safe_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return {"status": "success", "message": f"Content appended to '{filename}'."}
    except Exception as e:
        return {"error": f"Failed to append to file: {e}"}

@tool
def delete_file(filename: str):
    """
    Deletes a specified file.

    Args:
        filename: The path to the file to delete.
    """
    safe_path = _resolve_safe_path(filename)
    if not safe_path:
        return {"error": "Access denied. Cannot delete outside of the current working directory."}

    if not safe_path.is_file():
        return {"error": f"File not found: '{filename}'"}

    try:
        os.remove(safe_path)
        return {"status": "success", "message": f"File '{filename}' deleted."}
    except Exception as e:
        return {"error": f"Failed to delete file: {e}"}
