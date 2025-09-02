# import re
# import os
# import yaml

import click

from .main import *
from .config import *


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def workspace(env):
    """subcommands for managing workspaces for swarmtube"""
    # banner("User", env.__dict__)
    pass


@workspace.command()
@click.option("--path", default=None)
@click.pass_obj
def new(env, path):
    """Create a new workspace for swarmtube"""
    # force config loading
    config.callback()

    build_workspace(path)


@workspace.command()
@click.pass_obj
def list(env):
    """Find and list existing workspaces for swarmtube"""
    # force config loading
    config.callback()

    # TODO: implement
