"""
JSON pretty-printing with themes and streaming support.
"""

import json
import sys
from typing import Any, Optional

from colorama import init as colorama_init
from . import themes, utils

# Initialize colorama (for Windows + ANSI reset safety)
colorama_init(autoreset=True)


def is_json_string(s: str) -> bool:
    """
    Check if the given string is valid JSON.

    Args:
        s: Input string.

    Returns:
        bool: True if valid JSON, False otherwise.
    """
    try:
        json.loads(s)
        return True
    except Exception:
        return False


def _truncate_data(data: Any, max_items: Optional[int]) -> Any:
    """Recursively truncate lists and dicts based on max_items."""
    if max_items is None:
        return data

    if isinstance(data, list):
        if len(data) > max_items:
            return data[:max_items] + [f"... {len(data) - max_items} more items ..."]
        return [ _truncate_data(x, max_items) for x in data ]

    if isinstance(data, dict):
        if len(data) > max_items:
            keys = list(data.keys())[:max_items]
            truncated = {k: _truncate_data(data[k], max_items) for k in keys}
            truncated[f"... {len(data) - max_items} more keys ..."] = ""
            return truncated
        return {k: _truncate_data(v, max_items) for k, v in data.items()}

    return data


def pjson(
    data: Any,
    *,
    theme: str = "default",
    stream: bool = False,
    indent: int = 2,
    max_items: Optional[int] = None,
    file: Optional[Any] = None,
    **kwargs,
) -> None:
    """
    Pretty-print JSON-like objects.

    Args:
        data: The object to serialize as JSON.
        theme: Color theme to use (from `themes.py`).
        stream: If True, stream line-by-line instead of building the whole string in memory.
        indent: Indentation level for JSON output.
        max_items: Maximum number of items/keys per list/dict (nested truncation supported).
        file: Optional file-like object to print to (default: sys.stdout).
        **kwargs: Passed to `json.dumps`.
    """
    file = file or sys.stdout
    theme_colors = themes.get_theme(theme)

    def colorize(s: str) -> str:
        return utils.colorize_json(s, theme_colors)

    # Apply truncation if needed
    if max_items is not None:
        data = _truncate_data(data, max_items)

    if stream:
        encoder = json.JSONEncoder(indent=indent, **kwargs)
        for chunk in encoder.iterencode(data):
            file.write(colorize(chunk))
        file.write("\n")
        return

    # Normal mode
    try:
        formatted = json.dumps(data, indent=indent, **kwargs)
    except (TypeError, ValueError) as e:
        file.write(f"[PrintCraft JSON Error] {e}\n")
        return

    file.write(colorize(formatted) + "\n")
