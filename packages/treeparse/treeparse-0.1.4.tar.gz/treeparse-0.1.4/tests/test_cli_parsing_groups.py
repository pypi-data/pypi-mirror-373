import pytest
import sys
from treeparse import cli, command, argument, option, group


def test_group_argument_propagation():
    called = [False]

    def callback(id: int, name: str):
        called[0] = True
        assert id == 123
        assert name == "test"

    add_cmd = command(
        name="add", callback=callback, arguments=[argument(name="name", arg_type=str)]
    )

    user_group = group(
        name="user", arguments=[argument(name="id", arg_type=int)], commands=[add_cmd]
    )

    app = cli(name="test", subgroups=[user_group])

    sys.argv = ["test", "user", "123", "add", "test"]
    app.run()
    assert called[0]


def test_group_argument_in_help(capsys):
    def callback(id: int, name: str):
        pass

    cmd = command(
        name="add", callback=callback, arguments=[argument(name="name", arg_type=str)]
    )

    g = group(
        name="user", arguments=[argument(name="id", arg_type=int)], commands=[cmd]
    )

    app = cli(name="test", subgroups=[g], show_types=True)

    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "user [ID, int]" in captured.out


# @pytest.mark.skip("spurious fail")
def test_group_option_inheritance():
    called = []

    def callback(name: str, verbose: bool):
        called.append((name, verbose))

    cmd = command(
        name="greet",
        callback=callback,
        arguments=[argument(name="name", arg_type=str)],
    )
    grp = group(
        name="user",
        commands=[cmd],
        options=[option(flags=["--verbose"], arg_type=bool, default=False)],
    )
    app = cli(name="test", subgroups=[grp])

    # Test with option
    sys.argv = ["test", "user", "--verbose", "true", "greet", "Alice"]
    app.run()
    assert called == [("Alice", True)]

    # Test without option
    called.clear()
    sys.argv = ["test", "user", "greet", "Bob"]
    app.run()
    assert called == [("Bob", False)]


def test_group_arg_example():
    called = []

    def callback(name: str, user_id: int):
        called.append((name, user_id))

    cmd = command(
        name="process",
        callback=callback,
        arguments=[argument(name="name", arg_type=str)],
    )
    grp = group(
        name="user",
        commands=[cmd],
        arguments=[argument(name="user_id", arg_type=int)],
    )
    app = cli(name="test", subgroups=[grp])

    sys.argv = ["test", "user", "456", "process", "Charlie"]
    app.run()
    assert called == [("Charlie", 456)]
