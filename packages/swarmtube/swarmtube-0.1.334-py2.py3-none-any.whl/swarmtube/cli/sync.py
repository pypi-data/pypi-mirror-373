import asyncio

# import re
# import os
# import yaml

import click

import uvloop

from syncmodels.storage import YamlStorage, DualStorage
from syncmodels.syncmodels import SyncModel

from ..definitions import RAW_NS, APP_NS

from .main import *
from .config import *

from ..logic.crawler import SwarmtubeCrawler as Crawler


@main.group(context_settings=CONTEXT_SETTINGS)
@click.pass_obj
def sync(env):
    """subcommands for manage workspaces for glbot"""
    # banner("User", env.__dict__)


@sync.command()
@click.pass_obj
@click.option("--fibers", default=3)
@click.option("--config_path", default="./config.yaml")
@click.option("--raw_path", default=RAW_NS)
@click.option("--alt_storage_path", default=f"db/{APP_NS}")
@click.option("--include", multiple=True, default=[])
@click.option("--exclude", multiple=True, default=[])
def models(env, config_path, fibers, raw_path, alt_storage_path, include, exclude):
    """Sync models from remote system"""
    # force config loading
    config.callback()

    async def _main():
        alt_storage = DualStorage(url=alt_storage_path)
        syncmodel = [
            SyncModel(
                config_path=config_path,
                storage=None,
                alt_storage=alt_storage,
            )
        ]
        if raw_path:
            # add a new storage to save the 3rd party system in raw format
            raw_storage = YamlStorage(url=raw_path)
        else:
            raw_storage = None

        crawler = Crawler(
            syncmodel=syncmodel,
            raw_storage=raw_storage,
            fibers=fibers,
            include=include,
            exclude=exclude,
        )
        await crawler.run()

    uvloop.install()
    asyncio.run(_main())
