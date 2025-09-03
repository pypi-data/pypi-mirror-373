# plugins.py
"""
Atikin Plugin System

Features:
- Load plugins via entry points (`atikin_plugins.*`)
- Add new plugins dynamically
- List all available plugins
"""

import importlib
import sys
from importlib.metadata import entry_points
from typing import Dict, Callable

_PLUGIN_NAMESPACE = "atikin_plugins"

def load_plugins() -> Dict[str, Callable]:
    """
    Load all plugins registered under the 'atikin_plugins' entry point namespace.
    Returns a dict: {plugin_name: plugin_callable}
    """
    plugins: Dict[str, Callable] = {}

    eps = entry_points()
    # Python >=3.10 uses select by group
    if hasattr(eps, "select"):
        plugin_eps = eps.select(group=_PLUGIN_NAMESPACE)
    else:
        plugin_eps = eps.get(_PLUGIN_NAMESPACE, [])

    for ep in plugin_eps:
        try:
            plugin = ep.load()
            plugins[ep.name] = plugin
        except Exception as e:
            print(f"Failed to load plugin {ep.name}: {e}", file=sys.stderr)

    return plugins


def add_plugin(module_name: str, plugin_name: str):
    """
    Dynamically add a plugin (for testing/development without reinstall).
    Usage: atikin plugin add myplugin
    """
    try:
        module = importlib.import_module(module_name)
        print(f"Plugin '{plugin_name}' loaded from module '{module_name}'")
        return module
    except ModuleNotFoundError:
        print(f"Module '{module_name}' not found")
        return None


def list_plugins():
    """
    List all registered plugins
    """
    plugins = load_plugins()
    if plugins:
        print("Available Atikin plugins:")
        for name in plugins.keys():
            print(f"  - {name}")
    else:
        print("No plugins found.")


# Example usage
if __name__ == "__main__":
    print("Listing plugins:")
    list_plugins()

    print("\nAdding a plugin dynamically:")
    add_plugin("myplugin", "myplugin")
