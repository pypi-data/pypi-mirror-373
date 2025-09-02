import pytest
import sys
from treeparse import cli, command, argument, option


def test_choices_option(capsys):
    called = [False]
    captured_level = None

    def callback(level: int):
        nonlocal captured_level
        called[0] = True
        captured_level = level

    cmd = command(
        name="set-level",
        callback=callback,
        options=[option(flags=["--level"], arg_type=int, choices=[2, 3, 4])],
    )
    app = cli(name="test", commands=[cmd], show_types=True)
    # Test valid choice
    sys.argv = ["test", "set-level", "--level", "3"]
    app.run()
    assert called[0]
    assert captured_level == 3
    # Test invalid choice
    sys.argv = ["test", "set-level", "--level", "5"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out
    # Test help output
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "--level: int (2|3|4)" in captured.out


def test_choices_argument(capsys):
    called = [False]
    captured_choice = None

    def callback(choice: str):
        nonlocal captured_choice
        called[0] = True
        captured_choice = choice

    cmd = command(
        name="choose",
        callback=callback,
        arguments=[argument(name="choice", arg_type=str, choices=["a", "b", "c"])],
    )
    app = cli(name="test", commands=[cmd], show_types=True)
    # Test valid choice
    sys.argv = ["test", "choose", "b"]
    app.run()
    assert called[0]
    assert captured_choice == "b"
    # Test invalid choice
    sys.argv = ["test", "choose", "d"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "invalid choice" in captured.out
    # Test help output
    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "[CHOICE, str (a|b|c)]" in captured.out


def test_default_against_choices():
    def callback(opt: int):
        pass

    # Valid default
    option(flags=["--opt"], arg_type=int, default=3, choices=[2, 3, 4])
    cmd = command(
        name="test",
        callback=callback,
        options=[option(flags=["--opt"], arg_type=int, default=3, choices=[2, 3, 4])],
    )
    app = cli(name="test", commands=[cmd])
    app._validate()  # Should not raise

    # Invalid default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            options=[
                option(flags=["--opt"], arg_type=int, default=5, choices=[2, 3, 4])
            ],
        )
        app = cli(name="test", commands=[cmd])
        app._validate()
    assert "Default value 5 not in choices [2, 3, 4]" in str(exc.value)
