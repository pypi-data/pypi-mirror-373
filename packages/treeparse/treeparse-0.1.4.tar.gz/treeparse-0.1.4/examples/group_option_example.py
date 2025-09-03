"""Simple example demonstrating group-level options used in commands."""

from treeparse import cli, group, command, option, argument


def greet(name: str, message: str):
    """Greet a user with a custom message."""
    print(f"Hello, {name}! {message}")


def farewell(name: str, message: str):
    """Say farewell with a custom message."""
    print(f"Goodbye, {name}! {message}")


greet_cmd = command(
    name="greet",
    help="Greet someone",
    callback=greet,
    arguments=[argument(name="name", arg_type=str)],
)

farewell_cmd = command(
    name="farewell",
    help="Say farewell",
    callback=farewell,
    arguments=[argument(name="name", arg_type=str)],
)

user_group = group(
    name="user",
    help="User interaction commands",
    commands=[greet_cmd, farewell_cmd],
    options=[
        option(
            flags=["--message", "-m"],
            arg_type=str,
            help="Custom message to include",
            default="Have a great day!",
        )
    ],
)

app = cli(
    name="group_option_example",
    help="Example of group options propagated to commands",
    subgroups=[user_group],
)


def main():
    """Run the CLI application."""
    app.run()


if __name__ == "__main__":
    main()
