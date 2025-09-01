# printcraft/logging_formatter.py

"""
Logging Formatter for Printcraft
Integrates Printcraft pretty-printers into Python's logging system.
"""

import logging
from .core import pcraft


class PrintCraftFormatter(logging.Formatter):
    """
    A logging formatter that uses Printcraft to format log messages.

    Examples:
        >>> import logging
        >>> from printcraft import PrintCraftFormatter
        >>> logger = logging.getLogger("demo")
        >>> handler = logging.StreamHandler()
        >>> handler.setFormatter(PrintCraftFormatter())
        >>> logger.addHandler(handler)
        >>> logger.info({"event": "startup", "status": "ok"})
    """

    def __init__(self, fmt=None, datefmt=None, style="%", pretty=True, color=False):
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)
        self.pretty = pretty
        self.color = color

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        try:
            # Try pretty-printing structured data
            pcraft(msg, pretty=self.pretty, color=self.color)
            return ""  # printing handled by Printcraft
        except Exception:
            # Fallback to normal logging
            return super().format(record)
