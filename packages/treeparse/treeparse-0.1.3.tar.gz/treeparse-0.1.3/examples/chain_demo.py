from treeparse import cli, command, chain, argument

called = []


def step1(x: int):
    called.append(f"step1: {x}")
    print(f"Called step1 with {x}")


def step2(y: str):
    called.append(f"step2: {y}")
    print(f"Called step2 with {y}")


cmd1 = command(
    name="step1",
    help="First step",
    callback=step1,
    arguments=[argument(name="x", arg_type=int)],
)

cmd2 = command(
    name="step2",
    help="Second step",
    callback=step2,
    arguments=[argument(name="y", arg_type=str)],
)

chain_cmd = chain(name="pipeline", sort_key=100, chained_commands=[cmd1, cmd2])

app = cli(
    name="chain_demo",
    help="Demo of command chaining",
    commands=[cmd1, cmd2, chain_cmd],
    show_types=True,
)


def main():
    app.run()


if __name__ == "__main__":
    main()
