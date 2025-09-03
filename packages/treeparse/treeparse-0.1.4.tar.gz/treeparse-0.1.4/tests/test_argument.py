import pytest
from typing import List
from treeparse import argument


def test_argument_model():
    arg = argument(name="test", arg_type=int, help="Test arg")
    assert arg.name == "test"
    assert arg.arg_type is int


def test_command_validation_list_arg():
    def callback(words: List[str]):
        pass

    from treeparse import command

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    cmd.validate()  # Should not raise


def test_command_validation_list_mismatch():
    def callback(words: str):
        pass

    from treeparse import command

    cmd = command(
        name="echo",
        callback=callback,
        arguments=[argument(name="words", nargs="*", arg_type=str)],
    )
    with pytest.raises(ValueError) as exc:
        cmd.validate()
    assert "type mismatch" in str(exc.value)


def test_command_validation_choices_default():
    def callback(arg1: int):
        pass

    from treeparse import command

    # Valid default
    cmd = command(
        name="test",
        callback=callback,
        arguments=[argument(name="arg1", arg_type=int, default=3, choices=[1, 2, 3])],
    )
    cmd.validate()  # Should not raise

    # Invalid default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            arguments=[
                argument(name="arg1", arg_type=int, default=4, choices=[1, 2, 3])
            ],
        )
        cmd.validate()
    assert "Default value 4 not in choices [1, 2, 3]" in str(exc.value)


def test_command_validation_list_choices_default():
    def callback(args: List[int]):
        pass

    from treeparse import command

    # Valid list default
    cmd = command(
        name="test",
        callback=callback,
        arguments=[
            argument(
                name="args", nargs="*", arg_type=int, default=[1, 2], choices=[1, 2, 3]
            )
        ],
    )
    cmd.validate()  # Should not raise

    # Invalid list default
    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            arguments=[
                argument(
                    name="args",
                    nargs="*",
                    arg_type=int,
                    default=[1, 4],
                    choices=[1, 2, 3],
                )
            ],
        )
        cmd.validate()
    assert "Default value 4 not in choices [1, 2, 3]" in str(exc.value)
