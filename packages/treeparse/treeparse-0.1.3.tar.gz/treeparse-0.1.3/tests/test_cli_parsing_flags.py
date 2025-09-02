import pytest
import sys
from treeparse import cli, command, option


def test_option_short_long_flag_order():
    captured_output = None

    def callback(output: str):
        nonlocal captured_output
        captured_output = output

    opt = option(flags=["-o", "--output"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    # Validate should pass with 'output' as param name
    app._validate()  # Should not raise

    # Run with short flag
    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"

    # Run with long flag
    sys.argv = ["test", "cmd", "--output", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_long_short_order():
    captured_output = None

    def callback(output: str):
        nonlocal captured_output
        captured_output = output

    opt = option(flags=["--output", "-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    app._validate()  # Should not raise

    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"

    sys.argv = ["test", "cmd", "--output", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_short_only():
    captured_output = None

    def callback(o: str):
        nonlocal captured_output
        captured_output = o

    opt = option(flags=["-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    app._validate()  # Should not raise

    sys.argv = ["test", "cmd", "-o", "file.txt"]
    app.run()
    assert captured_output == "file.txt"


def test_option_name_mismatch_short_only():
    def callback(output: str):
        pass

    opt = option(flags=["-o"], arg_type=str)
    cmd = command(name="cmd", options=[opt], callback=callback)
    app = cli(name="test", commands=[cmd])

    with pytest.raises(ValueError) as exc:
        app._validate()
    assert "name mismatch" in str(exc.value)
