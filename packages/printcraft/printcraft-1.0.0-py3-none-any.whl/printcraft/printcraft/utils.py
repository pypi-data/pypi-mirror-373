# printcraft/utils.py

"""
Utility functions for PrintCraft.
Shared helpers for iteration, truncation, and safe formatting.
"""

import json
from typing import Any
import re

def colorize_json(s: str, theme: dict) -> str:
    """
    Apply ANSI color codes to a JSON string based on type.
    theme: dict with keys 'key', 'string', 'number', 'reset'
    """
    if not theme:
        return s

    # Colors for different JSON components
    key_color = theme.get("key", "")
    string_color = theme.get("string", "")
    number_color = theme.get("number", "")
    reset = theme.get("reset", "")

    # Color keys: "key":
    s = re.sub(r'(".*?")(\s*:)', lambda m: f"{key_color}{m.group(1)}{reset}{m.group(2)}", s)

    # Color string values: "value"
    s = re.sub(r'(:\s*)("(?:\\.|[^"])*")', lambda m: f"{m.group(1)}{string_color}{m.group(2)}{reset}", s)

    # Color numbers
    s = re.sub(r'(:\s*)(\d+(\.\d+)?)', lambda m: f"{m.group(1)}{number_color}{m.group(2)}{reset}", s)

    # Color booleans and null
    s = re.sub(r'(:\s*)(true|false|null)', lambda m: f"{m.group(1)}{number_color}{m.group(2)}{reset}", s, flags=re.IGNORECASE)

    return s

def is_iterable(obj: Any) -> bool:
    """Check if object is iterable (list, tuple, dict, set) but not a string."""
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def is_json_string(s: str) -> bool:
    """Check if the string is valid JSON."""
    try:
        json.loads(s)
        return True
    except Exception:
        return False

def is_json_like(obj):
    """Return True if obj is a dict or list"""
    return isinstance(obj, (dict, list))


def safe_str(obj: Any, max_len: int = 100) -> str:
    """
    Convert object to string safely.
    Truncate if longer than max_len.
    """
    try:
        s = str(obj)
        return s if len(s) <= max_len else s[: max_len - 1] + "…"
    except Exception:
        return f"<Unrepresentable object: {type(obj).__name__}>"


def truncate_list(lst: list, max_items: int = 10) -> list:
    """
    Return a truncated version of a list with a note if truncated.
    """
    try:
        if len(lst) > max_items:
            return lst[:max_items] + [f"… {len(lst) - max_items} more items …"]
        return lst
    except Exception:
        return ["<Error truncating list>"]


def truncate_dict(d: dict, max_items: int = 10) -> dict:
    """
    Return a truncated version of a dict with a note if truncated.
    """
    try:
        if len(d) > max_items:
            keys = list(d.keys())[:max_items]
            truncated = {k: d[k] for k in keys}
            truncated[f"… {len(d) - max_items} more keys …"] = ""
            return truncated
        return d
    except Exception:
        return {"<Error truncating dict>": ""}
    
def truncate_json(obj: Any, max_items: int = 10) -> Any:
    """
    Truncate JSON-like objects (dict or list) to max_items.
    Works recursively for nested structures.
    """
    if isinstance(obj, list):
        return truncate_list(obj, max_items)
    elif isinstance(obj, dict):
        return truncate_dict(obj, max_items)
    else:
        return obj

