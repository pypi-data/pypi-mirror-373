import pytest
from treeparse import chain, command, argument


def test_chain_validation():
    def cb1(a: int):
        pass

    def cb2(b: str):
        pass

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="b", arg_type=str)]
    )
    chain_obj = chain(name="chain", chained_commands=[cmd1, cmd2])
    chain_obj.validate()  # Should not raise

    # Check generated help
    assert chain_obj.help == "cmd1 ➜ cmd2"

    # Check effective args
    assert len(chain_obj.effective_arguments) == 2
    assert chain_obj.effective_arguments[0].name == "a"
    assert chain_obj.effective_arguments[1].name == "b"


def test_chain_conflict():
    def cb1(a: int):
        pass

    def cb2(a: str):
        pass

    cmd1 = command(
        name="cmd1", callback=cb1, arguments=[argument(name="a", arg_type=int)]
    )
    cmd2 = command(
        name="cmd2", callback=cb2, arguments=[argument(name="a", arg_type=str)]
    )
    chain_obj = chain(name="chain", chained_commands=[cmd1, cmd2])
    with pytest.raises(ValueError) as exc:
        _ = chain_obj.effective_arguments
    assert "Conflicting argument dest 'a'" in str(exc.value)
