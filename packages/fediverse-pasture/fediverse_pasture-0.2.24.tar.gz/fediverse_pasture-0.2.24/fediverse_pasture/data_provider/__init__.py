# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
import tomli_w
import tomllib
from typing import Tuple, List

from bovine import BovineActor
from bovine.activitystreams import Actor

from .generate import generate_one_actor, generate_possible_actors
from .models import ActorData


@dataclass
class DataProvider:
    """Provides the data about actors to various applications"""

    one_actor: ActorData = field(
        metadata={"description": "User in one actor and as an application actor"}
    )
    possible_actors: List[ActorData] = field(
        metadata={"description": "The list of actors used for verify_actor"}
    )

    def save(self):
        data = {
            "one_actor": self.one_actor.model_dump(exclude_none=True),
            "possible_actors": [
                x.model_dump(exclude_none=True) for x in self.possible_actors
            ],
        }

        with open("data.toml", "wb") as fp:
            tomli_w.dump(data, fp)

    @staticmethod
    def load():
        with open("data.toml", "rb") as fp:
            data = tomllib.load(fp)

        one_actor = ActorData(**(data["one_actor"]))
        possible_actors = [ActorData(**x) for x in data["possible_actors"]]

        return DataProvider(one_actor=one_actor, possible_actors=possible_actors)

    @staticmethod
    def generate(with_possible_actors=True):
        one_actor = generate_one_actor()
        if with_possible_actors:
            possible_actors = generate_possible_actors()
        else:
            possible_actors = []
        return DataProvider(one_actor=one_actor, possible_actors=possible_actors)

    @staticmethod
    def generate_and_load(only_generate_config):
        if only_generate_config:
            dp = DataProvider.generate()
            dp.save()
            exit(0)

        try:
            dp = DataProvider.load()
        except Exception:
            dp = DataProvider.generate()
            dp.save()

        return dp


def bovine_actor_for_actor_data(
    actor_id: str, data: ActorData
) -> Tuple[BovineActor, Actor]:
    """Builds the corresponding bovine actor and actor data

    :param actor_id: The actor id to be used, e.g. `https://pasture_one_actor/actor`
    :param data: The actor data
    :return: A tuple, where the first object is the Actor performing actions, and the second one the data object.
    """
    key_pair = data.key_pairs[0]
    bovine_actor = BovineActor(
        actor_id=actor_id,
        public_key_url=f"{actor_id}#{key_pair.name}",
        secret=key_pair.private,
    )

    actor_object = Actor(
        id=actor_id,
        preferred_username=data.user_part,
        name="Test Actor",
        inbox=f"{actor_id}/inbox",
        outbox=f"{actor_id}/outbox",
        public_key=key_pair.public,
        public_key_name=key_pair.name,
        summary=data.summary,
    )

    return bovine_actor, actor_object
