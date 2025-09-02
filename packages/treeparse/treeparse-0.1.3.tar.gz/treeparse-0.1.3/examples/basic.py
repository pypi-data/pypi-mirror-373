from treeparse import cli, command, group, argument


def hello():
    print("Hello, world!")


def hello1(name: str):
    print(f"Hello, {name}!")


app = cli(
    name="basic",
    help="A basic CLI example.",
    commands=[
        command(name="hello", help="Print hello world.", callback=hello, sort_key=-100)
    ],
    subgroups=[
        group(
            name="example",
            help="An example group.",
            commands=[
                command(
                    name="hello",
                    help="Print hello world from the group.",
                    callback=hello1,
                    arguments=[
                        argument(name="name", arg_type=str, sort_key=0),
                    ],
                )
            ],
        )
    ],
)


def main():
    app.run()


if __name__ == "__main__":
    main()
