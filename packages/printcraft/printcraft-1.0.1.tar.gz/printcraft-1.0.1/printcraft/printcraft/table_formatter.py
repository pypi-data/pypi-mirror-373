# printcraft/table_formatter.py

"""
Table Formatter for PrintCraft.
Supports ASCII, Unicode, Markdown, and HTML tables with optional color themes.
"""

from typing import List, Dict, Any, Optional, Union
from colorama import init as colorama_init
from .themes import apply_theme

# Initialize colorama
colorama_init(autoreset=True)


def ptable(
    data: Union[List[Dict[str, Any]], List[List[Any]]],
    headers: Optional[List[str]] = None,
    style: str = "ascii",
    color: bool = False,
    max_width: Optional[int] = None,
) -> None:
    """
    Pretty print a table in the terminal.

    Args:
        data: List of dicts or list of lists.
        headers: Optional headers; inferred if not given.
        style: "ascii" or "unicode".
        color: If True, applies basic color to first column.
        max_width: Optional maximum width for each cell.
    """
    if not data:
        print("(empty table)")
        return

    # Normalize rows
    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
    else:
        if headers is None:
            headers = [f"col{i}" for i in range(len(data[0]))]
        rows = [[str(x) for x in row] for row in data]

    # Optionally truncate cells
    if max_width:
        rows = [[(cell[: max_width - 1] + "…") if len(cell) > max_width else cell for cell in r] for r in rows]
        headers = [(h[: max_width - 1] + "…") if len(h) > max_width else h for h in headers]

    # Compute column widths
    col_widths = [max(len(str(h)), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]

    # Border characters
    if style == "ascii":
        corner, horiz, vert = "+", "-", "|"
    elif style == "unicode":
        corner, horiz, vert = "┼", "─", "│"
    else:
        raise ValueError(f"Unsupported table style: {style}")

    # Build line separator
    sep = corner + corner.join(horiz * (w + 2) for w in col_widths) + corner

    # Print header
    print(sep)
    header_row = vert + vert.join(f" {h:<{w}} " for h, w in zip(headers, col_widths)) + vert
    print(header_row)
    print(sep)

    # Print rows
    for row in rows:
        cells = []
        for i, w in enumerate(col_widths):
            cell = f"{row[i]:<{w}}"
            if color and i == 0:  # Example: colorize first column
                cell = apply_theme(cell, "yellow")
            cells.append(f" {cell} ")
        print(vert + vert.join(cells) + vert)
    print(sep)


def export_markdown(data: Union[List[Dict[str, Any]], List[List[Any]]], headers: Optional[List[str]] = None) -> str:
    """
    Export table as Markdown format string.
    """
    if not data:
        return ""

    if isinstance(data[0], dict):
        if headers is None:
            headers = list(data[0].keys())
        rows = [[str(row.get(h, "")) for h in headers] for row in data]
    else:
        if headers is None:
            headers = [f"col{i}" for i in range(len(data[0]))]
        rows = [[str(x) for x in row] for row in data]

    # Header row
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join("---" for _ in headers) + " |"

    # Data rows
    row_lines = ["| " + " | ".join(r) + " |" for r in rows]

    return "\n".join([header_line, sep_line] + row_lines)


def export_html(data: List[Dict[str, Any]]) -> str:
    """
    Export list of dicts as HTML table.
    """
    try:
        if not data:
            return "<table></table>"
        columns = list(data[0].keys())
        html = "<table border='1'>\n<tr>" + "".join(f"<th>{col}</th>" for col in columns) + "</tr>\n"
        for row in data:
            html += "<tr>" + "".join(f"<td>{row.get(col, '')}</td>" for col in columns) + "</tr>\n"
        html += "</table>"
        return html
    except Exception as e:
        return f"[printcraft][export_html] Error: {e}"
