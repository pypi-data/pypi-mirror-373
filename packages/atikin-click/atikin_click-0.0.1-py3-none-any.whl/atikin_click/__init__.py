# src/atikin_click/__init__.py

__version__ = "0.1.0"

# Imports from our package
from .cli import CLI, default_cli
from .output import echo
try:
    from .progress import ProgressBar, Spinner
except ImportError:
    ProgressBar = Spinner = None
try:
    from .autocomplete import print_autocomplete_instructions
except ImportError:
    print_autocomplete_instructions = None

__all__ = [
    "CLI",
    "default_cli",
    "echo",
    "ProgressBar",
    "Spinner",
    "print_autocomplete_instructions",
    "__version__",
]
