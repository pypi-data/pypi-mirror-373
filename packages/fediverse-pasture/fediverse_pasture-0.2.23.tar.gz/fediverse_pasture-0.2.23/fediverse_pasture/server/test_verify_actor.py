# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp

import pytest
from unittest.mock import MagicMock, AsyncMock
from .verify_actor import ActorVerifier, can_be_resolved, remote_urls


@pytest.mark.parametrize(
    ["uri", "resolvable"],
    [
        ("http://localhost/actor", True),
        ("https://remote.example", True),
        ("@remote@something.example", False),
    ],
)
def test_can_be_resolved(uri, resolvable):
    assert can_be_resolved(uri) == resolvable


@pytest.mark.parametrize(
    "remote_uri", ["https://remote.example/actor", "http://localhost/actor"]
)
async def test_determine_remote_actor_uri(remote_uri):
    verifier = ActorVerifier([], remote_uri, "http://localhost", MagicMock())

    await verifier.determine_remote_actor_uri(AsyncMock())

    assert verifier.remote_actor_uri == remote_uri


async def test_determine_remote_remote_actor_uri_invalid():
    verifier = ActorVerifier([], "invalid", "http://localhost", MagicMock())

    await verifier.determine_remote_actor_uri(AsyncMock())


@pytest.fixture
async def client_session():
    async with aiohttp.ClientSession() as session:
        yield session


@pytest.mark.parametrize(["key", "url"], remote_urls.items())
async def test_remote_urls(client_session, key, url):
    async with client_session.get(url) as response:
        assert response.status == 200
