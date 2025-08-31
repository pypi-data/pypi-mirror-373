# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import json
from dataclasses import dataclass
import bovine
import logging


from fediverse_pasture.types import ApplicationAdapterForLastActivity

logger = logging.getLogger(__name__)


@dataclass
class MisskeyApplication:
    """Used to query a misskey application"""

    domain: str
    username: str
    session: aiohttp.ClientSession | None = None

    misskey_id: str | None = None

    async def determine_actor_uri(self):
        actor_uri, _ = await bovine.clients.lookup_uri_with_webfinger(
            self.session, f"acct:{self.username}@{self.domain}", f"http://{self.domain}"
        )
        return actor_uri

    async def determine_misskey_id(self):
        response = await self.session.post(
            f"http://{self.domain}/api/users/search",
            json={"query": "actor"},
            headers={"content-type": "application/json"},
        )
        users = await response.json()

        for user in users:
            if user.get("host") == "pasture-one-actor":
                return user.get("id")

    async def public_posts(self):
        if not self.misskey_id:
            self.misskey_id = await self.determine_misskey_id()

        response = await self.session.post(
            "http://misskey/api/users/notes",
            json={"userId": self.misskey_id},
            headers={"Authorization": "Bearer token"},
        )
        return await response.json()

    async def user_post_with_object_id(self, object_id: str):
        notes = await self.public_posts()

        for data in notes:
            if object_id in json.dumps(data):
                return data

    async def last_activity(self) -> ApplicationAdapterForLastActivity:
        actor_uri = await self.determine_actor_uri()

        return ApplicationAdapterForLastActivity(
            actor_uri=actor_uri,
            fetch_activity=self.user_post_with_object_id,
            application_name="misskey",
        )
