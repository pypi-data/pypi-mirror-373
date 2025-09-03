from basic import app as basic_app
from demo import app as demo_app
from list_demo import app as list_demo_app
from choice_demo import app as choice_demo_app
from treeparse import cli

basic_app.name = "basic"
basic_app.sort_key = 100

super_app = cli(
    name="basic_super",
    line_connect=True,
    theme="monochrome",
    help="A super CLI that includes the basic CLI as a sub-CLI.",
    subgroups=[basic_app, demo_app, list_demo_app, choice_demo_app],
)


def main():
    super_app.run()


if __name__ == "__main__":
    main()
