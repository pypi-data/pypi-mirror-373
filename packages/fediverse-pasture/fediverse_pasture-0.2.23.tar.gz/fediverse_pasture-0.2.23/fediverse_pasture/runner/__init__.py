# SPDX-FileCopyrightText: 2023-2025 Helge
#
# SPDX-License-Identifier: MIT

import asyncio
import logging
from aiohttp.client_exceptions import ClientResponseError
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List

from bovine import BovineActor
from bovine.activitystreams import (
    Actor,
    factories_for_actor_object,
)
from bovine.activitystreams.activity_factory import ActivityFactory
from bovine.activitystreams.object_factory import ObjectFactory
from bovine.activitystreams.utils import combine_as_list

from fediverse_pasture.types import ApplicationAdapterForLastActivity, MessageModifier

from .id_maker import create_make_id_for_actor_id

logger = logging.getLogger(__name__)


@dataclass
class ActivitySender:
    """The ActivitySender class serves as a way to coordinate the process
    of sending the same activity to multiple Fediverse applications.

    The basic process is

    * Create an Activity with a published timestamp stored in published
    * Send this activity to applications using `send`
    * Retrieve the result from said applications

    The usual way to create an ActivitySender is the `for_actor` method,
    i.e.

    ```python
    activity_sender = ActivitySender.for_actor(bovine_actor, actor_object)
    ```
    """

    activity_factory: ActivityFactory
    object_factory: ObjectFactory
    bovine_actor: BovineActor
    make_id: Callable

    published: datetime | None = field(default=None)
    note: dict | None = field(default=None)
    activity: dict | None = field(default=None)
    object_id: str | None = field(default=None)

    sleep_after_getting_inbox: bool = field(default=True)

    include_mention: bool = field(
        default=False,
        metadata={
            "description": "Set to True if the created Note should mention the target"
        },
    )

    replace_https_with_http: bool = field(
        default=False,
        metadata={
            "description": "Replaces 'https://' with 'http://' in the actor URI and the resolved inbox. Useful to handle applications not supporting a configuration value dedicated to handling the http based Fediverse."
        },
    )

    public_value: str = field(
        default="https://www.w3.org/ns/activitystreams#Public",
        metadata={
            "description": "The default value to use for public, see https://codeberg.org/funfedidev/python_fediverse_pasture/issues/41"
        },
    )

    def init_create_note(self, modifier: MessageModifier):
        """Sets activity to a Create for a Note. Here the Note is
        constructed from a skeleton by applying `modifier` to it.
        To successfully send the note to most applications, modifier
        should set the Note's content, i.e.

        ```python
        >>> from bovine.testing import actor
        >>> from unittest.mock import AsyncMock, Mock
        >>> actor_mock = Mock(id=actor["id"])
        >>> actor_mock.build.return_value = actor
        >>> sender = ActivitySender.for_actor(AsyncMock(), actor_mock)
        >>> sender.init_create_note(lambda x: {**x, "content": "text"})
        >>> sender.note
        {'type': 'Note',
            'attributedTo': 'http://actor.example',
            'to': ['https://www.w3.org/ns/activitystreams#Public'],
            'id': 'http://actor.example/object/...
            'published': '...
            'content': 'text'}

        ```

        This method can be used to create objects of other types
        by overriding "type".
        """
        self.object_id = self.make_id()

        note = self.object_factory.note(
            id=self.object_id,
            to={self.public_value},
        ).build()
        del note["@context"]
        self.note = modifier(note)
        self.published = datetime.fromisoformat(note["published"].removesuffix("Z"))

    async def send(self, remote: str):
        """Sends the activity to the remote user

        :param remote: Actor URI of the remote user"""

        if self.note is None:
            return

        note = {
            **self.note,
        }
        note["to"] = note["to"] + [remote]

        if self.include_mention:
            mention = {"type": "Mention", "href": remote}
            note["tag"] = combine_as_list(note.get("tag", []), [mention])

        create = self.activity_factory.create(
            note, id=self.make_id(activity=True)
        ).build()

        if "@context" in note:
            create["@context"] = note["@context"]
        else:
            create["@context"] = [
                create["@context"],
                {"Hashtag": "as:Hashtag", "sensitive": "as:sensitive"},
            ]
        self.activity = create

        try:
            remote_inbox = await self._resolve_inbox(remote)
            return await self.bovine_actor.post(remote_inbox, create)
        except ClientResponseError as e:
            logger.warning("Posting to inbox of %s failed with %s", remote, e.status)
            logger.exception(e)
            return None

    async def _resolve_inbox(self, remote: str) -> str:
        result = await self.bovine_actor.get(self.adjust_uri(remote))
        if not isinstance(result, dict) or "inbox" not in result:
            raise Exception(
                "Remote %s does not have an inbox, cannot post activity", remote
            )

        remote_inbox = self.adjust_uri(result["inbox"])

        if self.sleep_after_getting_inbox:
            #
            # See https://codeberg.org/helge/funfedidev/issues/138#issuecomment-1640700
            #
            await asyncio.sleep(0.1)

        return remote_inbox

    def adjust_uri(self, uri):
        if not self.replace_https_with_http:
            return uri

        return uri.replace("https://", "http://")

    @staticmethod
    def for_actor(bovine_actor: BovineActor, actor_object: Actor):
        """Initializes the Activity Sender object for a given BovineActor
        and the corresponding actor object"""
        activity_factory, object_factory = factories_for_actor_object(
            actor_object.build()
        )

        if actor_object.id is None:
            raise ValueError("Actor id should be part of actor object")

        return ActivitySender(
            activity_factory=activity_factory,
            object_factory=object_factory,
            bovine_actor=bovine_actor,
            make_id=create_make_id_for_actor_id(actor_object.id),
        )


@dataclass
class ActivityRunner:
    """Coordinates sending an activity to many applications through an ActivitySender
    instances"""

    activity_sender: ActivitySender = field(
        metadata={"description": " an activity sender"}
    )
    applications: List[ApplicationAdapterForLastActivity] = field(
        metadata={"description": "list of applications to run against"}
    )

    wait_time: float = field(
        default=0.5,
        metadata={
            "description": """Time in seconds between trying to fetch the activity from remote servers"""
        },
    )

    tries: int = field(
        default=20,
        metadata={
            "description": """Number of tries to fetch activity from remote servers"""
        },
    )

    skip_fetch: bool = field(
        default=False, metadata={"description": """Skips fetching the result"""}
    )

    async def fetch_activity(self, application, object_id):
        for _ in range(self.tries):
            result = await application.fetch_activity(object_id)
            if result:
                return result
            await asyncio.sleep(self.wait_time)

    async def run_for_modifier(self, modifier: Callable[[dict], dict]):
        """modifier has the same format as for ActivitySender

        :param modifier: modifies the base object being send"""
        self.activity_sender.init_create_note(modifier)

        async with asyncio.TaskGroup() as tg:
            for application in self.applications:
                tg.create_task(self.activity_sender.send(application.actor_uri))

        if self.skip_fetch:
            return

        await asyncio.sleep(self.wait_time)

        result = {"activity": self.activity_sender.activity}

        for application in self.applications:
            result[application.application_name] = await self.fetch_activity(
                application, self.activity_sender.object_id
            )

        return result
