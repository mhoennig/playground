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

def read_markdown_file(path: str) -> str:
    """
    Returns:
        Content of the markdown file or an empty string if not found
    """
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            print(f"using: {path}")
            return f.read()
                
    print(f"skipping: {path } -- not found")
    return "" 