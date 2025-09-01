"""
List/Tuple Formatter for PrintCraft.
Pretty-prints lists and tuples with optional index highlighting, truncation, and themes.
"""

from typing import Any, List, Tuple, Union, Optional
from .themes import apply_theme

DataSeq = Union[List[Any], Tuple[Any, ...]]


def plist(
    data: DataSeq,
    *,
    theme: str = "cyan",
    show_index: bool = True,
    max_width: Optional[int] = None,
    max_items: Optional[int] = None,
) -> None:
    """
    Pretty print a list or tuple.

    Args:
        data: List or tuple of items.
        theme: Color theme for indices.
        show_index: Whether to display numeric index.
        max_width: Optional max width for each value (truncated if exceeded).
        max_items: Maximum number of items to display (rest collapsed into a summary line).
    """
    if not data:
        print("(empty sequence)")
        return

    seq = list(data)

    # Apply truncation by item count
    if max_items is not None and len(seq) > max_items:
        seq = seq[:max_items]
        truncated = True
    else:
        truncated = False

    for idx, item in enumerate(seq):
        val = str(item)

        # Truncate long values
        if max_width and len(val) > max_width:
            val = val[: max_width - 1] + "…"

        if show_index:
            idx_str = apply_theme(f"[{idx}]", theme)
            print(f"{idx_str} {val}")
        else:
            print(val)

    # Add truncation note
    if truncated:
        print(apply_theme(f"... ({len(data) - max_items} more items)", theme))
