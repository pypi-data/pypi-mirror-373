# Atikin-Click

**Atikin-Click** — lightweight, developer-friendly CLI toolkit with autocomplete, colored output, progress bars & spinners.  

Developed by: **Atikin Verse**

[![PyPI version](https://img.shields.io/pypi/v/atikin-click)](https://pypi.org/project/atikin-click/)
[![Python Version](https://img.shields.io/pypi/pyversions/atikin-click)](https://pypi.org/project/atikin-click/)
[![License](https://img.shields.io/pypi/l/atikin-click)](https://github.com/atikinverse/atikin-click/blob/main/LICENSE)
[![Tests](https://github.com/atikinverse/atikin-click/actions/workflows/test.yml/badge.svg)](https://github.com/atikinverse/atikin-click/actions)

---

## Features

- Simple, lightweight CLI framework  
- Built-in colored output & rich integration  
- Progress bars & spinners  
- Autocomplete support for Bash/Zsh/Fish  
- Plugin system for custom commands  

---

## Quick Start

### CLI One-Liner

```bash
python -m atikin_click version
````

### Plugin Example

```bash
python -m atikin_click plugin add my_plugin
python -m atikin_click plugin run my_plugin
```

---

## Installation

Install via PyPI:

```bash
pip install atikin-click
```

For development:

```bash
git clone https://github.com/atikinverse/atikin-click.git
cd atikin-click
pip install -e .
```

### Requirements

* Python 3.8+
* Optional: `rich` for enhanced output

---

## Usage

### CLI Commands

```bash
# Check version
python -m atikin_click version

# Plugin commands
python -m atikin_click plugin list
python -m atikin_click plugin add my_plugin
python -m atikin_click plugin run my_plugin

# Shell completion
python -m atikin_click completion bash
```

### Python API

```python
from atikin_click.cli import default_cli

@default_cli.command("hello", help="Say hello")
def hello(name: str):
    print(f"Hello {name}")

# Run programmatically
default_cli.run(["hello", "Atikin"])
```

---

## Development

1. Create a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

2. Install development dependencies:

```bash
pip install -e .[dev]
```

3. Run tests:

```bash
pytest -q --tb=short
```

---

## Publishing to PyPI

1. Build the package:

```bash
python -m pip install --upgrade build
python -m build
```

2. Upload to PyPI:

```bash
pip install --upgrade twine
twine upload dist/*
```

3. Test installation:

```bash
pip install atikin-click
python -m atikin_click version
```

> Tip: Use [TestPyPI](https://test.pypi.org/) first for trial uploads:

```bash
twine upload --repository testpypi dist/*
```

---

## Contributing

* Fork the repository
* Create a branch for your feature/fix
* Run tests locally
* Submit a pull request

Report issues on [GitHub Issues](https://github.com/atikinverse/atikin-click/issues).

---

## FAQ / Troubleshooting

**Q:** `ImportError: cannot import name 'default_cli'`
**A:** Ensure you are not running from inside `src/`. Use the installed package or root folder.

**Q:** Plugin commands not showing output
**A:** Make sure plugin functions print or return values, CLI just triggers them.

---

## License

MIT License © Atikin Verse

---

## 🔗 Author

**Atikin Verse**
For more tools & libraries: [https://atikinverse.com](https://atikinverse.com)

---

## 🌐 Follow Us

| Platform  | Username    |
| --------- | ----------- |
| Facebook  | atikinverse |
| Instagram | atikinverse |
| LinkedIn  | atikinverse |
| Twitter/X | atikinverse |
| Threads   | atikinverse |
| Pinterest | atikinverse |
| Quora     | atikinverse |
| Reddit    | atikinverse |
| Tumblr    | atikinverse |
| Snapchat  | atikinverse |
| Skype     | atikinverse |
| GitHub    | atikinverse |

---

<div align="center">  
Made with ❤️ by the **Atikin Verse** 🚀  
</div>
```
