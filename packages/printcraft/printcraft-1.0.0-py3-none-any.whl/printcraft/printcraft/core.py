"""
Auto-detection logic for PrintCraft.

The `craft` function inspects Python objects and chooses the best
formatter automatically. Users can override detection with the `hint` parameter.
"""

from typing import Any, Optional

from .json_formatter import pjson
from .table_formatter import ptable
from .dict_formatter import pdict
from .list_formatter import plist
from .preview import ppreview
from . import utils


_FORMATTERS = {
    "pjson": pjson,
    "ptable": ptable,
    "pdict": pdict,
    "plist": plist,
    "ppreview": ppreview,
}


def pcraft(
    data: Any,
    *,
    hint: Optional[str] = None,
    preview: bool = False,
    **kwargs
) -> None:
    """
    Auto-detect the best pretty-printer for the given object.

    Args:
        data: Any Python object to format.
        hint: Optional override ("json", "table", "dict", "list", "preview").
        preview: Force compact preview mode.
        **kwargs: Extra options passed to the underlying formatter
                  (e.g., `max_items`, `theme`, `max_width`).

    Examples:
        >>> from printcraft import craft
        >>> craft([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        # Automatically prints as a table

        >>> craft(data, hint="json", max_items=5)
        # Forces JSON formatting, truncating to 5 items
    """
    if preview:
        return ppreview(data, **kwargs)

    if hint and hint in _FORMATTERS:
        return _FORMATTERS[hint](data, **kwargs)

    # Auto-detection logic
    if utils.is_json_like(data):
        return pjson(data, **kwargs)
    elif utils.is_tabular(data):
        return ptable(data, **kwargs)
    elif isinstance(data, dict):
        return pdict(data, **kwargs)
    elif isinstance(data, (list, tuple, set)):
        return plist(data, **kwargs)
    else:
        # fallback: preview mode
        return ppreview(data, **kwargs)
