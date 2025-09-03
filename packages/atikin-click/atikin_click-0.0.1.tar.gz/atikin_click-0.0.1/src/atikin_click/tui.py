# tui.py
"""
Text-based UI (TUI) scaffold for Atikin CLI using Rich
"""

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt
except ImportError:
    Console = None

console = Console() if Console else None

def start_tui():
    if not console:
        print("Rich library not installed. TUI unavailable.")
        return

    console.clear()
    console.print("[bold green]Welcome to Atikin TUI[/bold green]")

    while True:
        console.print("\n[bold cyan]Menu:[/bold cyan]")
        console.print("  1) List plugins")
        console.print("  2) Run plugin")
        console.print("  3) Exit")

        choice = Prompt.ask("Choose an option", choices=["1","2","3"], default="3")
        if choice == "1":
            console.print("Plugin listing placeholder")
        elif choice == "2":
            console.print("Plugin run placeholder")
        elif choice == "3":
            console.print("Exiting TUI...")
            break
