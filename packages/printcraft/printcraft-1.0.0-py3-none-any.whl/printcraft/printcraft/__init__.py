# printcraft/__init__.py

"""
PrintCraft - A modern Python pretty-printing library.

Public API re-exports:
    - json(...)     → Pretty-print JSON objects
    - table(...)    → Pretty-print tabular data
    - dict(...)     → Pretty-print dictionaries
    - list(...)     → Pretty-print lists/tuples
    - preview(...)  → Compact preview mode
    - craft(...)    → Auto-detect the best formatter
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
