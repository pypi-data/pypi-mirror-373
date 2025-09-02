from treeparse import cli, command


def hello():
    print("Hello, world!")


app = cli(
    name="theme_demo.py",
    help="Demo of color themes",
    theme="mononeon",  # Change to MONOCHROME or DEFAULT to see differences
    commands=[
        command(
            name="hello",
            help="Print hello world.",
            callback=hello,
        )
    ],
)


def main():
    app.run()


if __name__ == "__main__":
    main()
