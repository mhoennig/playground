"""
Utility functions for the Job Interview AI Agent.
"""
from typing import List
import os

def human_readable_list(items: List[str], quote: str = "") -> str:
    """Convert a list to a human-readable string."""
    if len(quote) > 0:
        items = [f'{quote}{item}{quote}' for item in items]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]

def read_markdown_file(base_name: str, default_content: str = "") -> str:
    """Read content from a markdown file with local override support.
    
    Args:
        base_name: Base name of the markdown file without suffix
        default_content: Content to return if no file is found
        
    Returns:
        Content of the markdown file or default_content if not found
    """
    for suffix in ["-local.md", "-default.md"]:
        path = f"{base_name}{suffix}"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                print(f"using: {path}")
                return f.read()
    print(f"not found: {base_name}-(local|default.md)")
    return default_content 