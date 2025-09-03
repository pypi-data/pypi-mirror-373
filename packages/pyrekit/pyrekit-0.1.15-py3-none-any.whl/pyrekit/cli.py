import sys
from pyrekit.handlers import setup, handle_script
from pyrekit.files import list_scripts

HELP_STRING = """Choose one of the flags to use pyreact:
    --setup <PROJ_NAME>: To setup the project from scratch
    --scripts: To list scripts
    --run <NAME>: To run scripts (if not specified it will use the run script)
    --build: to build the entire project with optimizations
"""


def get_input():
    """
    Get only the important part of the argv
    """
    if len(sys.argv) > 1:
        return sys.argv[1:]
    return []


def main():
    """
        Pyrekit entry point
    """

    entry = get_input()
    if len(entry) != 0:
        if entry[0] == "--setup" and len(entry) > 1:
            setup(AppName=entry[1])
        elif entry[0] == "--setup":
            setup(AppName="PyReact")
        elif entry[0] == "--scripts":
            list_scripts()
        elif entry[0] == "--run" and len(entry) > 1:
            handle_script(entry[1])
        elif entry[0] == "--run":
            handle_script("run")
        elif entry[0] == "--build":
            handle_script("build")
    else:
        print(HELP_STRING)
