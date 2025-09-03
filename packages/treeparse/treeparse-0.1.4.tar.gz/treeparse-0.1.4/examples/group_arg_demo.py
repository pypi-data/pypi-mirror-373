from treeparse import cli, group, command, argument


def add(name: str, id: int):
    print(f"Adding user {name} with ID {id}")


add_cmd = command(
    name="add",
    help="Add user",
    callback=add,
    arguments=[argument(name="name", arg_type=str)],
)

user_group = group(
    name="user",
    help="User commands",
    arguments=[argument(name="id", arg_type=int)],
    commands=[add_cmd],
)

app = cli(
    name="group_arg_demo.py",
    help="Demo of group arguments",
    subgroups=[user_group],
    show_types=True,
)


def main():
    app.run()


if __name__ == "__main__":
    main()
