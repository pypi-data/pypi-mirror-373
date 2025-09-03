"""Simple example demonstrating root-level flag option used in commands."""

from treeparse import cli, command, option, argument


def greet(name: str, verbose: bool):
    """Greet a user with optional verbosity."""
    print(f"Hello, {name}!")
    if verbose:
        print("(This is a verbose greeting from the root level)")


def farewell(name: str, verbose: bool):
    """Say farewell with optional verbosity."""
    print(f"Goodbye, {name}!")
    if verbose:
        print("(This is a verbose farewell from the root level)")


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

app = cli(
    name="root_option_example",
    help="Example of root-level flag option propagated to commands",
    commands=[greet_cmd, farewell_cmd],
    options=[
        option(
            flags=["--verbose", "-v"],
            arg_type=bool,
            default=False,
            help="Enable verbose output at root level",
        )
    ],
)


def main():
    """Run the CLI application."""
    app.run()


if __name__ == "__main__":
    main()
