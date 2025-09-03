import sys
import pytest
from treeparse import cli, group, command, argument, option


def create_demo_cli():
    app = cli(
        name="demo",
        help="This CLI provides commands to handle various tasks with subcommands for specific actions.",
        max_width=135,
        show_types=True,
    )

    def info(verbose: bool = False):
        pass

    info_cmd = command(
        name="info",
        help="Display CLI information.",
        callback=info,
        options=[
            option(
                flags=["--verbose", "-v"],
                arg_type=bool,
                default=False,
                help="Show detailed information.",
                sort_key=0,
            ),
        ],
    )
    app.commands.append(info_cmd)

    project = group(name="project", help="Manage project-related operations.")
    app.subgroups.append(project)

    user = group(name="user", help="Manage user-related operations.")
    app.subgroups.append(user)

    def add_user(name: str, email: str = None):
        pass

    add_cmd = command(
        name="add",
        help="Add a new user to the system.",
        callback=add_user,
        arguments=[
            argument(name="name", arg_type=str, sort_key=0),
        ],
        options=[
            option(
                flags=["--email", "-e"],
                help="Email address of the user",
                arg_type=str,
                sort_key=0,
            ),
        ],
    )
    user.commands.append(add_cmd)

    def list_users():
        pass

    list_cmd = command(
        name="list",
        help="List all users in the system.",
        callback=list_users,
    )
    user.commands.append(list_cmd)

    manage = group(name="manage", help="Manage user settings and permissions.")
    user.subgroups.append(manage)

    def set_role(
        role: str,
        user_id: str = None,
        reason: str = None,
        user_id_option: int = None,
        reason_option: str = None,
    ):
        pass

    set_role_cmd = command(
        name="set-role",
        help="Set a role for a user.",
        callback=set_role,
        arguments=[
            argument(name="role", arg_type=str, nargs="?", default=None, sort_key=0),
            argument(name="user_id", arg_type=str, nargs="?", default=None, sort_key=1),
            argument(name="reason", arg_type=str, nargs="?", default=None, sort_key=2),
        ],
        options=[
            option(
                flags=["--user-id", "-u"],
                dest="user_id_option",
                help="User ID to set role for (unspecified if not provided), where the help is really really long to test the wrapping of the lines in the CLI even if the terminal width is really wide it still tests it because it is just so very very long.",
                arg_type=int,
                sort_key=0,
            ),
            option(
                flags=["--reason", "-r"],
                dest="reason_option",
                help="Reason for setting the role",
                arg_type=str,
                sort_key=1,
            ),
        ],
    )
    manage.commands.append(set_role_cmd)

    def remove_role(role: str, user_id: str):
        pass

    remove_role_cmd = command(
        name="remove-role",
        help="Remove a role from a user.",
        callback=remove_role,
        arguments=[
            argument(name="role", arg_type=str, sort_key=0),
            argument(name="user_id", arg_type=str, sort_key=1),
        ],
    )
    manage.commands.append(remove_role_cmd)

    permissions = group(name="permissions", help="Manage user permissions.")
    manage.subgroups.append(permissions)

    set_permissions = group(name="set", help="Manage user permissions.")
    permissions.subgroups.append(set_permissions)

    def add_permission(user_id: str, permission: str):
        pass

    add_perm_cmd = command(
        name="add",
        help="Add a permission for a user.",
        callback=add_permission,
        arguments=[
            argument(name="user_id", arg_type=str, sort_key=0),
            argument(name="permission", arg_type=str, sort_key=1),
        ],
    )
    set_permissions.commands.append(add_perm_cmd)

    return app


@pytest.fixture
def mock_argv():
    original = sys.argv
    yield
    sys.argv = original


def test_demo_help(mock_argv, capsys):
    app = create_demo_cli()
    sys.argv = ["demo.py", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Usage: demo ...  (--json, -j, --help, -h)" in captured.out


def test_demo_user_manage_help(mock_argv, capsys):
    app = create_demo_cli()
    sys.argv = ["demo.py", "user", "manage", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Manage user settings and permissions." in captured.out


def test_demo_remove_role_help(mock_argv, capsys):
    app = create_demo_cli()
    sys.argv = ["demo.py", "user", "manage", "remove-role", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Remove a role from a user." in captured.out


def test_demo_add_permission_help(mock_argv, capsys):
    app = create_demo_cli()
    sys.argv = ["demo.py", "user", "manage", "permissions", "set", "add", "--help"]
    with pytest.raises(SystemExit):
        app.run()
    captured = capsys.readouterr()
    assert "Add a permission for a user." in captured.out
