"""
Advanced interactive prompts for Atikin-Click.

Features:
- prompt() → text input with default, validators, hidden input
- confirm() → yes/no confirmation
- choice() → select one from a list of options
- multi_choice() → select multiple options from a list
- Rich integration if available (pretty UI), else plain fallback
"""

import sys
from typing import Optional, Callable, List, Any

try:
    from rich.prompt import Prompt as RichPrompt
    from rich.prompt import Confirm as RichConfirm
    from rich.console import Console
    from rich.table import Table
    _HAS_RICH = True
    _console = Console()
except ImportError:
    _HAS_RICH = False
    _console = None

try:
    import getpass
except ImportError:
    getpass = None


def prompt(
    message: str,
    default: Optional[str] = None,
    hide_input: bool = False,
    validator: Optional[Callable[[str], Any]] = None,
    allow_empty: bool = False,
) -> str:
    """
    Prompt user for input.
    - Supports default values
    - hide_input=True → password mode
    - validator → function that validates input, may return converted value
    - allow_empty → if True, empty input is allowed
    """
    while True:
        if _HAS_RICH and not hide_input:
            ans = RichPrompt.ask(message, default=default)
        elif hide_input:
            if getpass is None:
                raise RuntimeError("getpass not available on this system")
            msg = f"{message} "
            if default:
                msg += f"[default hidden] "
            ans = getpass.getpass(msg).strip()
            if not ans and default is not None:
                ans = default
        else:
            msg = f"{message} "
            if default:
                msg += f"[{default}] "
            ans = input(msg).strip()
            if not ans and default is not None:
                ans = default

        if not ans and not allow_empty:
            if _HAS_RICH:
                _console.print("[red]Input cannot be empty[/red]")
            else:
                print("Input cannot be empty")
            continue

        if validator:
            try:
                return validator(ans)
            except Exception as e:
                if _HAS_RICH:
                    _console.print(f"[red]Invalid input:[/red] {e}")
                else:
                    print(f"Invalid input: {e}")
                continue
        return ans


def confirm(message: str, default: bool = True) -> bool:
    """
    Yes/No confirmation prompt.
    """
    if _HAS_RICH:
        return RichConfirm.ask(message, default=default)
    else:
        ans = input(f"{message} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if not ans:
            return default
        return ans in ("y", "yes")


def choice(message: str, options: List[str], default: Optional[int] = None) -> str:
    """
    Let user select from a list of options.
    Returns the chosen string.
    """
    if not options:
        raise ValueError("No options provided")

    while True:
        if _HAS_RICH:
            table = Table(title=message)
            table.add_column("No.", style="cyan", justify="right")
            table.add_column("Option", style="green")
            for i, opt in enumerate(options, start=1):
                table.add_row(str(i), opt)
            _console.print(table)
        else:
            print(message)
            for i, opt in enumerate(options, start=1):
                print(f"  {i}) {opt}")

        raw = input(f"Enter choice [1-{len(options)}]{' (default=' + str(default) + ')' if default else ''}: ").strip()

        if not raw and default is not None:
            return options[default - 1]

        try:
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass

        if _HAS_RICH:
            _console.print("[red]Invalid choice, try again.[/red]")
        else:
            print("Invalid choice, try again.")


def multi_choice(message: str, options: List[str], defaults: Optional[List[int]] = None) -> List[str]:
    """
    Let user select multiple options from a list.
    Returns a list of chosen strings.
    """
    if not options:
        raise ValueError("No options provided")
    defaults = defaults or []

    while True:
        if _HAS_RICH:
            table = Table(title=message)
            table.add_column("No.", style="cyan", justify="right")
            table.add_column("Option", style="green")
            for i, opt in enumerate(options, start=1):
                table.add_row(str(i), opt)
            _console.print(table)
        else:
            print(message)
            for i, opt in enumerate(options, start=1):
                print(f"  {i}) {opt}")

        raw = input(f"Enter choices as comma-separated numbers{' (defaults=' + ','.join(map(str, defaults)) + ')' if defaults else ''}: ").strip()
        if not raw and defaults:
            return [options[i-1] for i in defaults]

        try:
            indices = [int(x) for x in raw.split(",") if x.strip()]
            if all(1 <= i <= len(options) for i in indices):
                return [options[i-1] for i in indices]
        except ValueError:
            pass

        if _HAS_RICH:
            _console.print("[red]Invalid choices, try again.[/red]")
        else:
            print("Invalid choices, try again.")
