"""
Dict Formatter for PrintCraft.
Aligned pretty-printing of dictionaries with optional color and truncation.
"""

from typing import Any, Dict, Optional
from .themes import apply_theme


def pdict(
    data: Dict[Any, Any],
    *,
    theme: str = "default",
    max_width: Optional[int] = None,
    max_items: Optional[int] = None,
    align: str = "left",
) -> None:
    """
    Pretty print a dictionary with aligned keys.

    Args:
        data: Dictionary to format.
        theme: Color theme to use (see `themes.py`).
        max_width: Optional max width for values (truncated with ellipsis if exceeded).
        max_items: Maximum number of key-value pairs to display.
        align: "left" or "right" alignment for values.
    """
    if not data:
        print("(empty dict)")
        return

    # Convert to list of (key, value) pairs
    items = list(data.items())

    # Truncate items count
    truncated = False
    if max_items is not None and len(items) > max_items:
        items = items[:max_items]
        truncated = True

    # Stringify keys & values
    items = [(str(k), str(v)) for k, v in items]

    # Truncate long values
    if max_width:
        items = [
            (k, (v[: max_width - 1] + "…") if len(v) > max_width else v)
            for k, v in items
        ]

    # Compute padding for aligned keys
    key_width = max(len(k) for k, _ in items) if items else 0

    for k, v in items:
        key_str = apply_theme(f"{k:<{key_width}}", theme)
        if align == "right":
            val_str = f"{v:>{max_width}}" if max_width else v
        else:
            val_str = v
        print(f"{key_str} : {val_str}")

    # Add truncation note
    if truncated:
        print(apply_theme(f"... ({len(data) - max_items} more keys)", theme))
