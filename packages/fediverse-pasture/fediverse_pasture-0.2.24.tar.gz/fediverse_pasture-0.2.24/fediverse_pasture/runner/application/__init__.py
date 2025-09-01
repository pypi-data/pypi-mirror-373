# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from typing import Callable, Awaitable
from bovine.clients import lookup_uri_with_webfinger

from fediverse_pasture.types import (
    ApplicationAdapterForActor,
    ApplicationAdapterForLastActivity,
)


from .mastodon import MastodonApplication
from .misskey import MisskeyApplication
from .firefish import FirefishApplication
from .bovine import BovineApplication


async def actor_for_application(
    account_uri: str, application_name: str, session: aiohttp.ClientSession
) -> ApplicationAdapterForActor:
    """Creates a ApplicationAdapterForActor

    :param account_uri: The acct uri, e.g. `acct:user@domain`
    :param application_name: The name of the application
    :param session: the aiohttp ClientSession
    """

    domain = account_uri.split("@")[1]

    actor_uri, _ = await lookup_uri_with_webfinger(
        session, account_uri, f"http://{domain}"
    )

    if not actor_uri:
        raise ValueError(f"Actor not found with URI {account_uri}")

    return ApplicationAdapterForActor(
        actor_uri=actor_uri, application_name=application_name
    )


async def activity_for_mastodon(
    domain: str,
    username: str,
    access_token: str,
    session: aiohttp.ClientSession,
    application_name: str = "mastodon",
    determine_actor_uri: bool = False,
) -> ApplicationAdapterForLastActivity:
    """Creates a ApplicationAdapterForLastActivity object for connecting to
    mastodon. Example usage:

    ```python
    mastodon = await activity_for_mastodon("mastodon_web", "bob", "xxx", session)
    ```
    """

    actor_uri = None

    if determine_actor_uri:
        actor_uri, _ = await lookup_uri_with_webfinger(
            session, f"acct:{username}@{domain}", f"http://{domain}"
        )

    mastodon = MastodonApplication(
        domain=domain, access_token=access_token, username=username, actor_uri=actor_uri
    )

    return mastodon.last_activity(session, application_name=application_name)


async def activity_for_firefish(
    domain: str, username: str, session: aiohttp.ClientSession
) -> ApplicationAdapterForLastActivity:
    """Creates a ApplicationAdapterForLastActivity object for connecting to
    firefish. Example usage:

    ```python
    firefish = await activity_for_firefish("firefish_web", "admin", session)
    ```
    """
    firefish = FirefishApplication(domain=domain, username=username)

    return await firefish.last_activity(session)


def activity_for_mastodon_provider(
    domain: str,
    username: str,
    access_token: str,
    application_name: str = "mastodon",
    determine_actor_uri: bool = False,
) -> Callable[[aiohttp.ClientSession], Awaitable[ApplicationAdapterForLastActivity]]:
    def func(session):
        return activity_for_mastodon(
            domain,
            username,
            access_token,
            session,
            application_name=application_name,
            determine_actor_uri=determine_actor_uri,
        )

    return func


def activity_for_misskey_provider(
    domain: str,
    username: str,
) -> Callable[[aiohttp.ClientSession], Awaitable[ApplicationAdapterForLastActivity]]:
    def func(session: aiohttp.ClientSession):
        async def misskey():
            app = MisskeyApplication(domain, username, session=session)

            return await app.last_activity()

        return misskey()

    return func


def activity_for_bovine_provider(domain, username, secret):
    app = BovineApplication(domain=domain, username=username, secret=secret)

    def func(session):
        return app.last_activity(session)

    return func


async def firefish_app(session):
    return await activity_for_firefish("firefish_web", "admin", session)


async def mitra_app(session):
    async with session.post(
        "http://mitra/oauth/token",
        data={"grant_type": "password", "username": "admin", "password": "password"},
    ) as response:
        data = await response.json()

    return await activity_for_mastodon(
        "mitra", "admin", data["access_token"], session, application_name="mitra"
    )


async def hubzilla_app(session):
    app = await actor_for_application("admin@hubzilla", "hubzilla", session)
    app.application_name = "hubzilla"
    return app


async def custom_app(session):
    from custom import app_from_session

    return await app_from_session(session)


mastodon_likes = {
    application_name: activity_for_mastodon_provider(
        application_name, username, "token", application_name=application_name
    )
    for application_name, username in [
        ("mastodon", "hippo"),
        ("gotosocial", "cookie"),
        ("akkoma", "witch"),
        ("pleroma", "full"),
    ]
}


app_name_to_coroutine = {
    **mastodon_likes,
    "bovine": activity_for_bovine_provider(
        "bovine", "vanilla", "z3u2Yxcowsarethebestcowsarethebestcowsarethebest"
    ),
    "misskey": activity_for_misskey_provider("misskey", "kitty"),
    "mitra": mitra_app,
    "firefish": firefish_app,
    "hubzilla": hubzilla_app,
    "sharkey": activity_for_mastodon_provider(
        "sharkey",
        "willy",
        "token",
        determine_actor_uri=True,
        application_name="sharkey",
    ),
    "custom": custom_app,
}
"""Used to lookup the coroutine to get the application object"""
