# import re
# import os
# import yaml

import click

# from swarmtube.helpers import *
from swarmtube.cli.main import main, CONTEXT_SETTINGS
from swarmtube.cli.config import config

from swarmtube.definitions import DEFAULT_LANGUAGE, UID_TYPE

# TODO: include any logic from module core
# Examples
# from swarmtube.models import *
# from swarmtube.logic import Tagger
# from syncmodels.storage import Storage

# Import local inventory models
from swarmtube.models.task import SwarmtubeTask as Item
from swarmtube.models.task import SwarmtubeTaskRequest as Request
from swarmtube.models.task import SwarmtubeTaskResponse as Response

# ---------------------------------------------------------
# Dynamic Loading Interface / EP Exposure
# ---------------------------------------------------------
TAG = "Tasks"
DESCRIPTION = "Tasks CLI API"
API_ORDER = 10

# ---------------------------------------------------------
# Loggers
# ---------------------------------------------------------

from agptools.logs import logger

log = logger(__name__)


# ---------------------------------------------------------
# Task CLI port implementation
# ---------------------------------------------------------
@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def task(env):
    """subcommands for managing tasks for swarmtube"""
    # banner("User", env.__dict__)


submodule = task


@submodule.command()
@click.option("--path", default=None)
@click.pass_obj
def create(env, path):
    """Create a new task for swarmtube"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def read(env):
    """Find and list existing tasks for swarmtube"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def update(env):
    """Update and existing task for swarmtube"""
    # force config loading
    config.callback()

    # TODO: implement


@submodule.command()
@click.pass_obj
def delete(env):
    """Delete an existing task for swarmtube"""
    # force config loading
    config.callback()

    # TODO: implement
