# src/atikin_click/cli.py

import argparse
import inspect
import sys
import asyncio
from typing import Callable, Dict

from .output import echo
from .validators import ValidationError

class CLI:
    def __init__(self, prog: str = "atikin", description: str = None):
        self.prog = prog
        self.description = description
        self._commands: Dict[str, Dict] = {}

    def command(self, name: str = None, help: str = None):
        def decorator(func: Callable):
            cmd = name or func.__name__.replace("_", "-")
            self._commands[cmd] = {
                "func": func,
                "help": help or (func.__doc__ or ""),
                "signature": inspect.signature(func),
            }
            return func
        return decorator

    def _param_type(self, param: inspect.Parameter):
        return param.annotation if param.annotation is not inspect._empty else str

    def _build_parser(self):
        parser = argparse.ArgumentParser(prog=self.prog, description=self.description)
        subparsers = parser.add_subparsers(dest="command", required=True)

        # Register normal commands
        for cmd_name, meta in self._commands.items():
            sub = subparsers.add_parser(cmd_name, help=meta["help"])
            sig = meta["signature"]
            for pname, param in sig.parameters.items():
                if pname == "self":
                    continue
                ptype = self._param_type(param)
                if param.default is inspect._empty:
                    sub.add_argument(pname, type=ptype)
                else:
                    flag = f"--{pname.replace('_','-')}"
                    if isinstance(param.default, bool):
                        action = "store_true" if param.default is False else "store_false"
                        sub.add_argument(flag, action=action, help=f"{pname} (default={param.default})")
                    else:
                        sub.add_argument(flag, type=ptype, default=param.default)
            sub.set_defaults(_cmd=cmd_name)

        # Plugin commands
        plugin_parser = subparsers.add_parser("plugin", help="Manage plugins")
        plugin_sub = plugin_parser.add_subparsers(dest="action", required=True)
        plugin_sub.add_parser("list", help="List plugins")
        add_parser = plugin_sub.add_parser("add", help="Add plugin")
        add_parser.add_argument("name")
        run_parser = plugin_sub.add_parser("run", help="Run plugin")
        run_parser.add_argument("name")

        # Completion command
        completion_parser = subparsers.add_parser("completion", help="Shell completion")
        completion_parser.add_argument("shell", choices=["bash","zsh","fish"])

        return parser

    def run(self, argv=None):
        argv = argv if argv is not None else sys.argv[1:]
        parser = self._build_parser()

        # optional argcomplete
        try:
            import argcomplete
            argcomplete.autocomplete(parser)
        except Exception:
            pass

        args = parser.parse_args(argv)
        cmd = getattr(args, "_cmd", None)

        if cmd:
            meta = self._commands[cmd]
            func = meta["func"]
            ns = vars(args)
            kwargs = {k:v for k,v in ns.items() if k not in ("command","_cmd")}
            try:
                if asyncio.iscoroutinefunction(func):
                    asyncio.run(func(**kwargs))
                else:
                    result = func(**kwargs)
                    if isinstance(result,int):
                        return result
                return 0
            except ValidationError as ve:
                echo(f"Validation error: {ve}", err=True)
                return 4
            except TypeError as te:
                echo(f"Argument error: {te}", err=True)
                return 3
            except Exception as e:
                echo(f"Error running {cmd}: {e}", err=True)
                return 1

        # Handle plugin separately
        if getattr(args, "command", None) == "plugin":
            action = getattr(args, "action")
            name = getattr(args, "name", None)
            if action == "list":
                echo("No plugins found")
            elif action == "add" and name:
                echo(f"Plugin added: {name}")
            elif action == "run" and name:
                echo(f"Plugin running: {name}")
            else:
                echo("Missing plugin name", fg="red")
                return 2
            return 0

        # Completion command
        if getattr(args, "command", None) == "completion":
            shell = getattr(args, "shell")
            echo(f"Completion script for {shell} shell")
            return 0

        parser.print_help()
        return 2


# --------------------------
# default CLI instance
# --------------------------
default_cli = CLI(prog="atikin", description="Atikin-Click: small CLI toolkit")

# --------------------------
# Built-in version command
# --------------------------
@default_cli.command("version", help="Show Atikin-Click version")
def _version():
    from . import __version__
    echo(f"Atikin-Click {__version__}")
