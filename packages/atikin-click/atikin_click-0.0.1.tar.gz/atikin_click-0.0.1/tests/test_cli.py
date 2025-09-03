import pytest
from atikin_click.cli import default_cli

def test_version_command(capsys):
    rc = default_cli.run(["version"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Atikin-Click" in captured.out

def test_plugin_list(capsys):
    rc = default_cli.run(["plugin", "list"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "No plugins found" in captured.out

def test_plugin_add(capsys):
    rc = default_cli.run(["plugin", "add", "test_plugin"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Plugin added: test_plugin" in captured.out

def test_plugin_run(capsys):
    rc = default_cli.run(["plugin", "run", "test_plugin"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Plugin running: test_plugin" in captured.out
