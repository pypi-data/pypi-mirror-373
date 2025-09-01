# printcraft/__init__.py

"""
PrintCraft - A modern Python pretty-printing library.

Public API re-exports:
    - pjson(...)     → Pretty-print JSON objects
    - ptable(...)    → Pretty-print tabular data
    - pdict(...)     → Pretty-print dictionaries
    - plist(...)     → Pretty-print lists/tuples
    - ppreview(...)  → Compact preview mode
    - pcraft(...)    → Auto-detect the best formatter
    - PrintCraftFormatter → Logging formatter for integration
"""

from .json_formatter import pjson
from .table_formatter import ptable
from .dict_formatter import pdict
from .list_formatter import plist
from .preview import ppreview
from .core import pcraft
from .logging_formatter import PrintCraftFormatter

__all__ = [
    "pjson",
    "ptable",
    "pdict",
    "plist",
    "ppreview",
    "pcraft",
    "PrintCraftFormatter",
]
