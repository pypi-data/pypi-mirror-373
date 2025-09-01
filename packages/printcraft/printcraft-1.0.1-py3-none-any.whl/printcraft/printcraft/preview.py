# printcraft/preview.py

"""
Preview Formatter for PrintCraft.
Provides compact previews of large data structures.
"""

from typing import Any, Iterable, Dict, List, Tuple, Union
from .themes import apply_theme


def ppreview(
    data: Any,
    *,
    limit: int = 5,
    theme: str = "magenta",
    show_type: bool = True,
) -> None:
    """
    Print a compact preview of the data.

    Args:
        data: The object to preview (list, tuple, dict, set, str, etc.).
        limit: Number of items to show before truncating.
        theme: Theme used for ellipsis ("...").
        show_type: Whether to show the data type in the preview.
    """
    if data is None:
        print("(None)")
        return

    ellipsis = apply_theme("...", theme)

    if isinstance(data, (list, tuple, set)):
        seq = list(data)
        shown = seq[:limit]
        preview = ", ".join(str(x) for x in shown)
        if len(seq) > limit:
            preview += f", {ellipsis}"
        out = f"[{preview}]" if isinstance(data, list) else f"({preview})"

    elif isinstance(data, dict):
        items = list(data.items())[:limit]
        preview = ", ".join(f"{k}: {v}" for k, v in items)
        if len(data) > limit:
            preview += f", {ellipsis}"
        out = f"{{{preview}}}"

    elif isinstance(data, str):
        if len(data) > limit:
            out = repr(data[:limit])[:-1] + ellipsis + "'"
        else:
            out = repr(data)

    else:
        out = str(data)

    if show_type:
        print(f"<{type(data).__name__}> {out}")
    else:
        print(out)
