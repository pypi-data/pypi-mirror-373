"""Simple example demonstrating group-level arguments used in commands."""

from treeparse import cli, group, command, argument


def process(name: str, user_id: int):
    """Process a user with ID and name."""
    print(f"Processing user {name} with ID {user_id}")


def update(name: str, user_id: int):
    """Update a user with ID and name."""
    print(f"Updating user {name} with ID {user_id}")


process_cmd = command(
    name="process",
    help="Process a user",
    callback=process,
    arguments=[argument(name="name", arg_type=str)],
)

update_cmd = command(
    name="update",
    help="Update a user",
    callback=update,
    arguments=[argument(name="name", arg_type=str)],
)

user_group = group(
    name="user",
    help="User management commands",
    commands=[process_cmd, update_cmd],
    arguments=[
        argument(name="user_id", arg_type=int, help="User ID for the operation")
    ],
)

app = cli(
    name="group_arg_example",
    help="Example of group-level arguments propagated to commands",
    subgroups=[user_group],
)


def main():
    """Run the CLI application."""
    app.run()


if __name__ == "__main__":
    main()
