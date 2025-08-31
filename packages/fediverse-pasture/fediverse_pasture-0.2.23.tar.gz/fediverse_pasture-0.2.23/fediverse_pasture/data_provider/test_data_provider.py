# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from bovine import BovineActor
from bovine.activitystreams import Actor

from . import DataProvider, bovine_actor_for_actor_data


def test_actor_data():
    dp = DataProvider.generate()

    data = dp.one_actor.model_dump()

    assert data["actor_name"] == "actor"
    assert data["user_part"] == "actor"


def test_bovine_actor():
    dp = DataProvider.generate()

    actor, data = bovine_actor_for_actor_data("http://localhost/actor", dp.one_actor)

    assert isinstance(actor, BovineActor)
    assert isinstance(data, Actor)
