import pytest
from atikin_click.cli import default_cli  # import default_cli instance

# -------------------------
# Sync plugin test
# -------------------------
def test_add_sync_plugin(capsys):
    rc = default_cli.run(["plugin", "add", "sample_plugin"])
    out, err = capsys.readouterr()
    assert rc == 0
    assert "Plugin added: sample_plugin" in out

def test_run_sync_plugin(capsys):
    rc = default_cli.run(["plugin", "run", "hello"])
    out, err = capsys.readouterr()
    assert rc == 0
    assert "Plugin running: hello" in out

# -------------------------
# Async plugin test
# -------------------------
def test_run_async_plugin(capsys):
    rc = default_cli.run(["plugin", "run", "async_hello"])
    out, err = capsys.readouterr()
    assert rc == 0
    assert "Plugin running: async_hello" in out

# -------------------------
# REPL / completion simulation
# -------------------------
def test_repl_simulation(capsys):
    rc = default_cli.run(["completion", "bash"])
    out, err = capsys.readouterr()
    assert rc == 0
    assert "Completion script for bash shell" in out
