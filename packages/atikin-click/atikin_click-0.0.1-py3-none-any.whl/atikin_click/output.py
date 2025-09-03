import sys
import json
from typing import Optional, Any, List

_COLORS = {
    "black": "30", "red": "31", "green": "32", "yellow": "33",
    "blue": "34", "magenta": "35", "cyan": "36", "white": "37"
}

def _ansi(code: str) -> str:
    return f"\033[{code}m"

def _wrap(text: str, fg: Optional[str] = None, bold: bool = False, dim: bool = False) -> str:
    parts = []
    if bold:
        parts.append("1")
    if dim:
        parts.append("2")
    if fg and fg in _COLORS:
        parts.append(_COLORS[fg])
    if parts:
        start = _ansi(";".join(parts))
        end = _ansi("0")
        return f"{start}{text}{end}"
    return text

def echo(text: str, fg: Optional[str] = None, bold: bool = False, dim: bool = False, err: bool = False):
    out = sys.stderr if err else sys.stdout
    out.write(_wrap(text, fg=fg, bold=bold, dim=dim) + "\n")
    out.flush()
