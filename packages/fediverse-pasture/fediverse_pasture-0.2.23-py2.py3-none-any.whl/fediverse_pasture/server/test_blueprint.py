# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from quart import Quart

from fediverse_pasture.data_provider import DataProvider

from . import BlueprintForActors


@pytest.fixture
def client_one_actor():
    dp = DataProvider.generate(with_possible_actors=False)
    bfa = BlueprintForActors(actors=[dp.one_actor])

    app = Quart(__name__)
    app.register_blueprint(bfa.blueprint)

    yield app.test_client()


async def test_actor_webfinger(client_one_actor):
    response = await client_one_actor.get(
        "/.well-known/webfinger?resource=acct:actor@localhost"
    )

    assert response.status_code == 200


async def test_actor_get(client_one_actor):
    response = await client_one_actor.get("/actor")

    assert response.status_code == 200

    data = await response.get_json()

    assert isinstance(data, dict)


async def test_actor_not_found(client_one_actor):
    response = await client_one_actor.get("/other")

    assert response.status_code == 404


async def test_actor_post(client_one_actor):
    response = await client_one_actor.post("/actor/inbox", data={})

    assert response.status_code == 202
