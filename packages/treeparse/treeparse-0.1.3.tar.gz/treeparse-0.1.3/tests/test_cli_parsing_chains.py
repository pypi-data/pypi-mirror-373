import pytest
import sys
from treeparse import cli, command, argument, chain


def test_chain_execution():
    calls = []

    def cb1(a: int):
        calls.append(("cb1", a))

    def cb2(b: str):
        calls.append(("cb2", b))

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="b", arg_type=str)]
    )
    chain_obj = chain(name="chain", chained_commands=[cmd1, cmd2])
    app = cli(name="test", commands=[chain_obj])

    sys.argv = ["test", "chain", "42", "hello"]
    app.run()
    assert calls == [("cb1", 42), ("cb2", "hello")]


def test_chain_help(capsys):
    def cb1():
        pass

    def cb2():
        pass

    cmd1 = command(name="cmd1", callback=cb1)
    cmd2 = command(name="cmd2", callback=cb2)
    chain_obj = chain(name="chain", chained_commands=[cmd1, cmd2])
    app = cli(name="test", commands=[chain_obj])

    sys.argv = ["test", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "chain" in captured.out
    assert "cmd1 ➜ cmd2" in captured.out
