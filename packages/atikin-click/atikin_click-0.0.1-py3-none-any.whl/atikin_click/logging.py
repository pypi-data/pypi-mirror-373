# logging.py
"""
Atikin Logging System

Features:
- Verbosity flags: --verbose (shows debug), --quiet (suppress info/warn)
- Colored output (Rich if available)
- Levels: DEBUG, INFO, WARN, ERROR
"""

import sys
import logging

try:
    from rich.console import Console
    from rich.text import Text
    _HAS_RICH = True
    _console = Console()
except ImportError:
    _HAS_RICH = False
    _console = None

# Custom log levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARN = logging.WARNING
ERROR = logging.ERROR

# Default logger setup
_logger = logging.getLogger("atikin")
_logger.setLevel(DEBUG)
_handler = logging.StreamHandler(sys.stdout)
_formatter = logging.Formatter("[%(levelname)s] %(message)s")
_handler.setFormatter(_formatter)
_logger.addHandler(_handler)

# Verbosity control
_verbose = False
_quiet = False

def setup_logging(verbose: bool = False, quiet: bool = False):
    """
    Setup verbosity flags
    --verbose : show DEBUG messages
    --quiet   : suppress INFO and WARN messages
    """
    global _verbose, _quiet
    _verbose = verbose
    _quiet = quiet

def log_debug(message: str):
    if not _verbose or _quiet:
        return
    if _HAS_RICH:
        _console.print(f"[magenta][DEBUG][/magenta] {message}")
    else:
        _logger.debug(message)

def log_info(message: str):
    if _quiet:
        return
    if _HAS_RICH:
        _console.print(f"[blue][INFO][/blue] {message}")
    else:
        _logger.info(message)

def log_warn(message: str):
    if _quiet:
        return
    if _HAS_RICH:
        _console.print(f"[yellow][WARN][/yellow] {message}")
    else:
        _logger.warning(message)

def log_error(message: str):
    if _HAS_RICH:
        _console.print(f"[red][ERROR][/red] {message}")
    else:
        _logger.error(message)

# Example usage
if __name__ == "__main__":
    setup_logging(verbose=True)
    log_debug("Debug mode activated")
    log_info("Deployment started")
    log_warn("Config not found")
    log_error("Build failed")
