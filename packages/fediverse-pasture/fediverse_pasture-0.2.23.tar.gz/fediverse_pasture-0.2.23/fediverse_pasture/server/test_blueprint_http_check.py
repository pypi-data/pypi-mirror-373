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
    actor = dp.one_actor
    actor.requires_signed_get_for_actor = True
    actor.requires_signed_post_for_inbox = True
    bfa = BlueprintForActors(actors=[actor])

    app = Quart(__name__)
    app.register_blueprint(bfa.blueprint)

    yield app.test_client()


async def test_actor_get_unsigned(client_one_actor):
    response = await client_one_actor.get("/actor")

    assert response.status_code == 401


async def test_actor_post_unsigned(client_one_actor):
    response = await client_one_actor.post("/actor/inbox", data={})

    assert response.status_code == 401
