from treeparse import cli, group, command, option, argument


def greet(name: str, verbose: bool):
    print(f"Greeting {name}")
    if verbose:
        print("(in verbose mode)")


greet_cmd = command(
    name="greet",
    help="Greet someone",
    callback=greet,
    arguments=[argument(name="name", arg_type=str)],
)

user_group = group(
    name="user",
    help="User commands",
    commands=[greet_cmd],
    options=[
        option(
            flags=["--verbose", "-v"],
            arg_type=bool,
            default=False,
            help="Verbose output",
        )
    ],
)

app = cli(
    name="group_option_demo.py", help="Demo of group options", subgroups=[user_group]
)


def main():
    app.run()


if __name__ == "__main__":
    main()
