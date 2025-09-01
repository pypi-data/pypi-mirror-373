# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import click

from typing import Tuple
from contextlib import asynccontextmanager
from urllib.parse import urljoin

from bovine import BovineActor
from bovine.activitystreams import Actor

from .data_provider import (
    DataProvider,
    bovine_actor_for_actor_data,
)
from .server import assets_blueprint_for_directory
from .server.image_provider_blueprint import image_provider_blueprint
from .server.one_actor_app import app_for_data_provider
from .server.nodeinfo_blueprint import nodeinfo_blueprint

from .version import __version__


def bovine_actor_and_actor_object(domain: str) -> Tuple[BovineActor, Actor]:
    """Returns the BovineActor and the Actor object corresponding to the
    actor being served by one_actor

    :param domain: The domain the actor lives on
    :return: BovineActor and Actor object"""
    dp = DataProvider.load()

    actor_id = urljoin(domain, "/actor")

    return bovine_actor_for_actor_data(actor_id, dp.one_actor)


@asynccontextmanager
async def bovine_actor_and_session(
    domain: str = "http://pasture-one-actor",
):
    async with aiohttp.ClientSession() as session:
        bovine_actor, actor = bovine_actor_and_actor_object(domain)
        await bovine_actor.init(session=session)

        yield bovine_actor, actor, session


@click.command()
@click.option("--only_generate_config", default=False, is_flag=True)
@click.option(
    "--assets",
    default=None,
    help="Directory to serve assets from. Assets will be served under /assets/",
)
@click.option("--port", default=2909, help="port to run on")
@click.option("--reload", default=False, is_flag=True)
@click.option("--with_nodeinfo", default=False, is_flag=True)
def one_actor(only_generate_config, assets, port, reload, with_nodeinfo):
    print(f"fediverse pasture one_actor {__version__}")

    dp = DataProvider.generate_and_load(only_generate_config)

    app = app_for_data_provider(dp)

    app.register_blueprint(image_provider_blueprint, url_prefix="/images")

    if assets:
        app.register_blueprint(assets_blueprint_for_directory(assets))

    if with_nodeinfo:
        app.register_blueprint(nodeinfo_blueprint)

    app.run(port=port, host="0.0.0.0", use_reloader=reload)


if __name__ == "__main__":
    one_actor()
