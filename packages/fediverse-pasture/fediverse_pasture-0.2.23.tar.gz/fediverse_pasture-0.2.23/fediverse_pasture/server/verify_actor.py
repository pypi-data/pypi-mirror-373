# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import asyncio
import aiohttp
import logging
import secrets
import json
from typing import List
from urllib.parse import urlparse
from dataclasses import dataclass, field

from bovine.clients import lookup_uri_with_webfinger

from fediverse_pasture.data_provider import bovine_actor_for_actor_data
from fediverse_pasture.data_provider.models import ActorData
from fediverse_pasture.types import Message

logger = logging.getLogger(__name__)

remote_urls = {
    "documentation": "https://funfedi.dev/python_package/verify_actor/",
    "support_table": "https://funfedi.dev/support_tables/generated/verify_actor/",
    "repository": "https://codeberg.org/helge/funfedidev/",
}


def can_be_resolved(uri: str) -> bool:
    if uri.startswith("http://"):
        return True

    if uri.startswith("https://"):
        return True

    return False


@dataclass
class ActorVerifier:
    """Class implementing the logic to verify a remote actor"""

    actor_list: List[ActorData] = field(
        metadata={"description": "List of actors to run verification with"}
    )
    remote_uri: str = field(
        metadata={
            "description": "URI of the remote actor. If acct-uri, it is resolved using webfinger"
        }
    )
    domain: str = field(
        metadata={"description": "The domain the verification is done from"}
    )
    message: Message = field(
        metadata={"description": "Message object containing an event log"}
    )

    remote_actor_uri: str | None = None
    scheme: str = "http"

    timeout: int = field(
        default=20, metadata={"description": "The timeout for requests (in seconds)"}
    )

    async def verify(self, only: dict = {}):
        """Public interface, this method loops over the actors in `actor_list`
        and verifies using them if the remote_uri is accessible.

        Returns a dictionary with actor.actor_name as key and the
        result as value.

        This function creates it's own aiohttp.ClientSession"""
        async with aiohttp.ClientSession() as session:
            await self.determine_remote_actor_uri(session)
            result = {
                actor.actor_name: await self.verify_for_actor(session, actor)
                for actor in self.actor_list
                if actor.actor_name != "actor" and only.get(actor.actor_name, True)
            }
            result["webfinger"] = await self.check_webfinger_result(session)

            return result

    @property
    def main_actor(self) -> ActorData | None:
        for actor in self.actor_list:
            if actor.actor_name == "actor":
                return actor
        return None

    async def init_bovine_actor(self, actor, session):
        actor_id = f"{self.scheme}://{self.domain}/{actor.actor_name}"
        bovine_actor, _ = bovine_actor_for_actor_data(actor_id, actor)
        await bovine_actor.init(session=session)

        return bovine_actor

    async def check_webfinger_result(self, session):
        bovine_actor = await self.init_bovine_actor(self.main_actor, session)

        try:
            async with asyncio.timeout(self.timeout):
                actor = await bovine_actor.get(self.remote_actor_uri)
        except Exception as e:
            logger.exception(e)
            return False

        if actor is None:
            self.message.error("Failed to fetch actor")
            return False

        remote_actor_uri = actor.get("id", self.remote_actor_uri)

        preferred_username = actor.get("preferredUsername")

        self.message.add(f"Got preferredUsername {preferred_username}")
        if preferred_username is None:
            return False

        domain = urlparse(self.remote_actor_uri).netloc
        acct_uri = f"acct:{preferred_username}@{domain}"

        self.message.add(f"computed acct uri {acct_uri}")

        try:
            object_id, _ = await lookup_uri_with_webfinger(
                session, acct_uri, f"{self.scheme}://{domain}"
            )
        except Exception as e:
            logger.exception(e)
            return False
        self.message.add(f"Retrieved id {object_id} using webfinger")

        if object_id == remote_actor_uri:
            self.message.add("webfinger result matches expectations")

            return True

        return False

    async def verify_for_actor(self, session, actor):
        bovine_actor = await self.init_bovine_actor(actor, session)
        self.message.add(f"Running verification for {actor.actor_name}")

        if actor.requires_signed_post_for_inbox:
            return await self.fetch_remote_and_post_using_actor(bovine_actor)
        else:
            return await self.fetch_remote_and_post_using_session(session)

    async def fetch_remote_and_post_using_actor(self, bovine_actor):
        result = {"get_actor": False, "post_inbox": False}

        try:
            async with asyncio.timeout(self.timeout):
                actor = await bovine_actor.get(self.remote_actor_uri)
                if actor is None:
                    self.message.add(
                        f"Failed to retrieve actor {self.remote_actor_uri}"
                    )
                    return result

                inbox = actor.get("inbox")
                self.message.add(f"Got inbox {inbox}")

                if inbox:
                    result["get_actor"] = True
                    try:
                        try:
                            response = await bovine_actor.post(
                                inbox,
                                data={
                                    "@context": "https://www.w3.org/ns/activitystreams",
                                    "type": "Like",
                                    "actor": bovine_actor.actor_id,
                                    "id": bovine_actor.actor_id
                                    + secrets.token_urlsafe(8),
                                    "object": bovine_actor.actor_id,
                                },
                            )
                            self.message.add("Successfully posted to inbox with result")
                            self.message.add(response.status)
                            self.message.add((await response.text()))

                        except aiohttp.ClientResponseError as e:
                            if e.status == 400:
                                self.message.add(
                                    "Successfully posted to inbox but remote server\
    indicated a bad request"
                                )
                            else:
                                raise e

                        result["post_inbox"] = True
                    except Exception as e:
                        self.message.add("Failed to post to inbox")
                        self.message.add(repr(e))

        except Exception as e:
            self.message.add("Something went wrong")
            self.message.add(repr(e))

        return result

    async def resolve_inbox_using_session(self, session) -> str:
        async with asyncio.timeout(self.timeout):
            async with session.get(
                self.remote_actor_uri,
                headers={"accept": "application/activity+json"},
            ) as response:
                actor = json.loads(await response.text())
            inbox = actor.get("inbox")
            self.message.add(f"Got inbox {inbox}")
            return inbox

    async def fetch_remote_and_post_using_session(self, session):
        result = {"get_actor": False, "post_inbox": False}

        try:
            inbox = await self.resolve_inbox_using_session(session)
        except Exception as e:
            self.message.add("Something went wrong when fetching actor")
            self.message.add(repr(e))
            return result

        if inbox:
            result["get_actor"] = True
            try:
                async with asyncio.timeout(self.timeout):
                    async with session.post(
                        inbox,
                        data=json.dumps(
                            {
                                "@context": "https://www.w3.org/ns/activitystreams",
                                "type": "EchoRequest",
                            }
                        ),
                        headers={"content-type": "application/activity+json"},
                    ) as response:
                        self.message.add(f"Got {response.status} for unsigned POST")

                        if response.status < 400 and response.status > 100:
                            result["post_inbox"] = True
            except Exception as e:
                self.message.add("Something went wrong when posting to inbox")
                self.message.add(repr(e))
                return result

        return result

    async def determine_remote_actor_uri(self, session) -> None:
        """Used to resolve an acct-URI into the corresponding http/https-URI
        using webfinger"""
        if can_be_resolved(self.remote_uri):
            self.remote_actor_uri = self.remote_uri
            self.message.add(f"Can fetch actor from {self.remote_uri}")
            return

        self.message.add(f"Need to resolve {self.remote_uri} to actor object id")

        if self.remote_uri.startswith("acct:"):
            acct_uri = self.remote_uri
        else:
            self.message.add("Not in account uri format")

            if self.remote_uri[0] == "@":
                acct_uri = "acct:" + self.remote_uri[1:]
            else:
                acct_uri = "acct:" + self.remote_uri

        if "@" not in acct_uri:
            self.message.add(f"Computed invalid account URI {acct_uri}")
            return
        domain = acct_uri.split("@")[1]

        self.message.add(f"Resolving {acct_uri} using webfinger")

        try:
            object_id, _ = await lookup_uri_with_webfinger(
                session, acct_uri, f"{self.scheme}://{domain}"
            )
        except Exception as e:
            logger.exception(e)
            return

        self.message.add(f"Resolved to {object_id}")
        self.remote_actor_uri = object_id
