import pytest
import sys
from treeparse import cli, command, argument, option, chain, group


def test_cli_build_parser():
    app = cli(name="test", help="Test CLI")
    parser = app.build_parser()
    assert parser.prog == "test"


def test_cli_validation_error(capsys):
    def callback(arg1: int):
        pass

    cmd = command(
        name="test", callback=callback, arguments=[argument(name="arg2", arg_type=int)]
    )
    app = cli(name="test", commands=[cmd])
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "name mismatch" in captured.out


def test_cli_with_command():
    called = [False]

    def callback():
        called[0] = True

    cmd = command(name="cmd", callback=callback)
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "cmd"]
    app.run()
    assert called[0]


def test_cli_list_arg():
    called = [False]
    captured_words = []

    def callback(words):
        called[0] = True
        captured_words.extend(words)

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "echo", "hello", "world"]
    app.run()
    assert called[0]
    assert captured_words == ["hello", "world"]


def test_cli_list_option():
    called = [False]
    captured_tags = []

    def callback(tags):
        called[0] = True
        captured_tags.extend(tags)

    cmd = command(
        name="tag",
        callback=callback,
        options=[option(flags=["--tags"], nargs="+", arg_type=str)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "tag", "--tags", "tag1", "tag2"]
    app.run()
    assert called[0]
    assert captured_tags == ["tag1", "tag2"]


def test_cli_bool_arg():
    called = [False]
    captured_bool = None

    def callback(flag: bool):
        nonlocal captured_bool
        called[0] = True
        captured_bool = flag

    cmd = command(
        name="booltest",
        callback=callback,
        arguments=[argument(name="flag", arg_type=bool)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "booltest", "true"]
    app.run()
    assert called[0]
    assert captured_bool is True


def test_cli_list_bool_option():
    called = [False]
    captured_flags = []

    def callback(flags):
        called[0] = True
        captured_flags.extend(flags)

    cmd = command(
        name="listbool",
        callback=callback,
        options=[option(flags=["--flags"], nargs="+", arg_type=bool)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "listbool", "--flags", "true", "false"]
    app.run()
    assert called[0]
    assert captured_flags == [True, False]


def test_cli_bool_option():
    called = [False]
    captured_flag = None

    def callback(flag: bool):
        nonlocal captured_flag
        called[0] = True
        captured_flag = flag

    cmd = command(
        name="flagtest",
        callback=callback,
        options=[option(flags=["--flag", "-f"], arg_type=bool, default=False)],
    )
    app = cli(name="test", commands=[cmd])
    sys.argv = ["test", "flagtest", "--flag", "true"]
    app.run()
    assert called[0]
    assert captured_flag is True


def test_super_cli():
    called = [False]

    def callback():
        called[0] = True

    sub_cmd = command(name="subcmd", callback=callback)
    sub_app = cli(name="sub", help="Sub CLI", commands=[sub_cmd])
    super_app = cli(name="test_super", help="Super CLI", subgroups=[sub_app])
    sys.argv = ["test_super", "sub", "subcmd"]
    super_app.run()
    assert called[0]
