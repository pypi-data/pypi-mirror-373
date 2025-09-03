# testing.py
"""
Async-compatible testing helper for Atikin CLI
"""

import sys
import io
import asyncio
from contextlib import redirect_stdout
from inspect import iscoroutinefunction

def run_cli(cli, args: list[str]) -> tuple[int, str]:
    """
    Run a CLI instance with given arguments and capture output.

    Args:
        cli: CLI instance (e.g., default_cli)
        args: list of arguments as strings

    Returns:
        tuple[int, str]: (return code, captured output)
    """
    f = io.StringIO()
    rc = 0

    # Redirect stdout to capture all prints/echoes
    with redirect_stdout(f):
        # Check if CLI.run is async
        run_method = cli.run
        if iscoroutinefunction(run_method):
            rc = asyncio.run(run_method(args))
        else:
            # Run normally
            rc = run_method(args)

    output = f.getvalue()
    return rc, output
