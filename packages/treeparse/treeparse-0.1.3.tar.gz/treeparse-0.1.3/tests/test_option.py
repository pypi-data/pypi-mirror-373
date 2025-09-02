import pytest
from treeparse import option


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


def test_command_validation_flag_with_choices():
    def callback(flag: bool):
        pass

    from treeparse import command

    with pytest.raises(ValueError) as exc:
        cmd = command(
            name="test",
            callback=callback,
            options=[option(flags=["--flag"], is_flag=True, choices=[True, False])],
        )
        cmd.validate()
    assert "Choices not applicable for flag option '--flag'" in str(exc.value)
