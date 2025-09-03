import pytest
from treeparse import option, cli


def test_option_model():
    opt = option(flags=["--test", "-t"], arg_type=str, help="Test option")
    assert opt.flags == ["--test", "-t"]
    assert opt.arg_type is str


def test_option_dest_prefer_long():
    opt = option(flags=["-o", "--output"])
    assert opt.get_dest() == "output"


def test_option_dest_short_only():
    opt = option(flags=["-o"])
    assert opt.get_dest() == "o"


def test_option_dest_long_first():
    opt = option(flags=["--output", "-o"])
    assert opt.get_dest() == "output"


def test_option_dest_with_explicit_dest():
    opt = option(flags=["-o", "--output"], dest="outfile")
    assert opt.get_dest() == "outfile"


def test_option_dest_no_flags():
    opt = option(flags=[])
    with pytest.raises(ValueError):
        opt.get_dest()


def test_command_validation_choices_default():
    def callback(opt: int):
        pass

    from treeparse import command

    # Valid default
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
