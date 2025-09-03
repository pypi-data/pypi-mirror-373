# config.py
"""
Config loader for Atikin-Click tools

Features:
- Auto-load from .env
- YAML and JSON support
- Environment variables override config file values
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    import yaml
except ImportError:
    yaml = None
import json

# Load .env if python-dotenv is installed
if load_dotenv:
    load_dotenv()


def load_config(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load config from YAML or JSON file.
    Environment variables override file values.
    """
    config: Dict[str, Any] = {}

    if file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file {file_path} not found")

        if path.suffix.lower() in (".yaml", ".yml"):
            if not yaml:
                raise ImportError("PyYAML not installed. Install with `pip install pyyaml`")
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        elif path.suffix.lower() == ".json":
            with open(path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            raise ValueError("Unsupported config file format. Use .yaml/.yml or .json")

    # Override with environment variables if present
    for key in config.keys():
        env_val = os.getenv(key.upper())
        if env_val is not None:
            config[key] = env_val

    return config


def get(key: str, default: Any = None) -> Any:
    """
    Get a config value, first checking environment variables
    """
    return os.getenv(key.upper(), default)


# Example usage
if __name__ == "__main__":
    cfg = load_config("config.yml")
    print("Loaded config:", cfg)
    print("Specific value:", get("some_key", "default_value"))
