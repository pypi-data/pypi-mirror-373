import pytest
import sys
from treeparse import cli, command, argument, option


def test_display_name_includes_py(capsys):
    app = cli(name="test.py", help="Test CLI")
    sys.argv = ["test.py", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: test.py ...  (--json, -j, --help, -h)" in captured.out
    assert app.display_name == "test.py"


def test_display_name_no_py():
    app = cli(name="test", help="Test CLI")
    assert app.display_name == "test"


def test_super_cli_with_py_name(capsys):
    called = [False]

    def callback():
        called[0] = True

    sub_cmd = command(name="subcmd", callback=callback)
    sub_app = cli(name="sub.py", help="Sub CLI", commands=[sub_cmd])
    super_app = cli(name="test_super", help="Super CLI", subgroups=[sub_app])

    # Check help output
    sys.argv = ["test_super", "--help"]
    with pytest.raises(SystemExit):
        super_app.run()
    captured = capsys.readouterr()
    assert "sub.py " in captured.out  # display_name with .py

    # Check execution
    sys.argv = ["test_super", "sub.py", "subcmd"]
    super_app.run()
    assert called[0]

    # Check invalid call without .py
    sys.argv = ["test_super", "sub", "subcmd"]
    with pytest.raises(SystemExit):
        super_app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out


def test_help_with_arguments(capsys):
    def callback(name: str):
        pass

    cmd = command(
        name="greet",
        help="Greet someone.",
        arguments=[argument(name="name", arg_type=str)],
        callback=callback,
    )
    app = cli(name="test", commands=[cmd])

    sys.argv = ["test", "greet", "John", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: test greet [ARGS...] ...  (--json, -j, --help, -h)" in captured.out
    assert "Greet someone." in captured.out
