from treeparse import cli, command, option


def set_level(level: int):
    print(f"Level set to {level}")


app = cli(
    name="choice_demo.py",
    show_defaults=True,
    show_types=True,
    help="""Demo of choices for options.
    line two
    line [red]three[/red]
    """,
    commands=[
        command(
            name="set-level",
            help="Set the level.",
            callback=set_level,
            options=[
                option(
                    flags=["--level", "-l"],
                    arg_type=int,
                    choices=[2, 3, 4],
                    help="Level to set",
                    default=3,
                )
            ],
        )
    ],
)


def main():
    app.run()


if __name__ == "__main__":
    main()
