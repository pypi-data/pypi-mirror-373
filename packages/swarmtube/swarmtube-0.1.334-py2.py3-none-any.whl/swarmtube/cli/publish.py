import os
import yaml

import click

from rich import print

# from swarmtube.helpers import *
from swarmtube.cli.main import main, CONTEXT_SETTINGS
from swarmtube.cli.config import config

# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
RED = "\033[31;1;4m"
GREEN = "\033[32;1;4m"
YELLOW = "\033[33;1;4m"
BLUE = "\033[34;1;4m"
PINK = "\033[35;1;4m"

RESET = "\033[0m"


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def publish(env):
    """A new group named 'config' nested to 'main' group
    Whenever a 'config' subcommand is called, this code
    will be executed before and load or create a config file
    by default.
    """

    try:
        load_config(env)

    except Exception as why:
        # If load_config fails, then create a clean one.
        print(f"{why}")

        setdefault(
            env,
            "includes",
            {
                r"swarmtube/.*\.yaml$": None,
            },
        )
        setdefault(
            env,
            "excludes",
            {},
        )
        setdefault(
            env,
            "folders",  # Not regexp
            {
                #'~/Documents': None,
                #'~/workspace': None,
                ".": None,
            },
        )
        setdefault(
            env,
            "resource",
            os.path.join(env.home, "resources.yaml"),
        )
        setdefault(
            env,
            "role",
            os.path.join(env.home, "roles.yaml"),
        )
        # if old != env.__dict__:
        # save_config(env)

        save_config(env)
    return env


@publish.command()
@click.pass_obj
def world(env):

    banner("Hello World!")
    data = {
        "name": "world",
        "url": "http://localhost",
    }

    print(data)
