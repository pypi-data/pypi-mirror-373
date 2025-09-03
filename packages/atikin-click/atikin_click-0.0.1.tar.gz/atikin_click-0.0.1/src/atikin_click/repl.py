# repl.py
"""
REPL mode for Atikin CLI
Interactive prompt with async support
"""

import asyncio
from logging import log_info, log_warn, log_error, log_debug
from cli import run_command

class AtikinREPL:
    def __init__(self, prompt="atikin> "):
        self.prompt = prompt
        self.running = True

    async def run_async_command(self, cmd: str):
        args = cmd.strip().split()
        if not args:
            return
        command = args[0]
        command_args = args[1:]
        try:
            # Try async first
            run_command(command)
        except Exception as e:
            log_error(f"Error: {e}")

    def start(self):
        log_info("Entering Atikin REPL. Type 'exit' or Ctrl-D to quit.")
        try:
            while self.running:
                try:
                    cmd = input(self.prompt).strip()
                except EOFError:
                    break
                if not cmd:
                    continue
                if cmd.lower() in ("exit", "quit"):
                    break
                asyncio.run(self.run_async_command(cmd))
        except KeyboardInterrupt:
            log_info("\nExiting REPL...")
        log_info("REPL session ended.")
