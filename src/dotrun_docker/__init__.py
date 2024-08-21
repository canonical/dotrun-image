#! /usr/bin/env python3

# Standard library
import os
import sys
from argparse import (
    REMAINDER,
    SUPPRESS,
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    RawTextHelpFormatter,
)
from importlib import metadata

# Packages
from termcolor import cprint

# Local
from dotrun_docker.models import Project

__version__ = metadata.version("dotrun-docker")


# Define available commands
# ===
class RawWithDefaultsFormatter(
    RawTextHelpFormatter, ArgumentDefaultsHelpFormatter
):
    pass


def get_commands():
    commands = (
        "The following commands have been provided by this project's "
        "package.json.\n\n{}".format(
            os.popen("yarn run --non-interactive").read()
        )
    )
    return commands


cli_parser = ArgumentParser(
    description=(
        "Containerized project-level dependency management and "
        "package.json commands"
    ),
    formatter_class=RawWithDefaultsFormatter,
    epilog=get_commands(),
)

# Options
cli_parser.add_argument(
    "-s",
    "--skip-install",
    action="store_true",
    default=False,
    help="Don't check for python or node dependencies before running",
)
cli_parser.add_argument(
    "-e",
    "--env",
    action="append",
    default=SUPPRESS,
    help=(
        "Environment variables to use when running commands.\n"
        "These will override what's in .env or .env.local"
    ),
)

# Main command
cli_parser.add_argument(
    "command",
    help=(
        "A package.json command to run with `yarn run XXX` inside dotrun.\n"
        "Simply typing `dotrun` will run `yarn run start`.\n"
        "\n"
        "Or a special command - one of:\n"
        "- version: Print the version\n"
        "- exec [command]: Execute a command or open a bash shell"
        " within the dotrun context\n"
        "- install: Reinstall node and python dependencies\n"
        "- clean: Run `yarn run clean` and remove all dotrun files\n"
        "- clean-cache: Delete the cache, including yarn & pip caches\n"
    ),
    nargs="?",
    default="start",
)
cli_parser.add_argument("remainder", nargs=REMAINDER, help=SUPPRESS)


def cli(args=None):
    """
    Parse the command-line arguments
    """

    if args is None:
        args = sys.argv[1:]

    arguments = cli_parser.parse_args(args)
    command = arguments.command

    # Commands that don't need dependencies
    if command == "version":
        print(f"dotrun-docker v{__version__}")
        sys.exit()

    # Compile list of environment variables
    env_extra = {}

    if "env" in arguments:
        for env_string in arguments.env:
            key, value = env_string.split("=")
            env_extra[key] = value

    # Prepare dotrun object
    path = os.getcwd()

    dotrun = Project(path=path, env_extra=env_extra)

    # Clean runs before install
    if command == "clean":
        return dotrun.clean()

    if command == "clean-cache":
        return dotrun.exec(["rm", "-rf", f"{os.environ['HOME']}/.cache"])

    if command == "exec":
        return dotrun.exec(arguments.remainder or ["bash"])

    if command == "install":
        return dotrun.install(force=True)

    if not arguments.skip_install:
        dotrun.install(force=False)

    # By default, run a yarn script
    if command == "":
        command = "start"
    if dotrun.has_script(command):
        try:
            return dotrun.yarn_run(command, arguments.remainder)
        finally:
            dotrun.terminate_background_processes()
    else:
        cprint(
            f"\n[ `{command}` script not found in `package.json` ]\n",
            "red",
        )
        cli_parser.print_usage()
        sys.exit(1)
