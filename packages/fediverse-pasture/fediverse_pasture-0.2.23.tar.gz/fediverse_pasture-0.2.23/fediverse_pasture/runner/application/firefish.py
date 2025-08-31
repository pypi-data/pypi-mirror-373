# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from dataclasses import dataclass
from datetime import datetime
import bovine
import logging


from fediverse_pasture.types import ApplicationAdapterForLastActivity

logger = logging.getLogger(__name__)


@dataclass
class FirefishApplication:
    """Used to query a firefish application"""

    domain: str
    username: str
    session: aiohttp.ClientSession | None = None
    token: str = "VvGrKxhpIzJ1PomJFTBObYWOELgGniVi"

    firefish_id: str | None = None

    async def determine_actor_uri(self):
        actor_uri, _ = await bovine.clients.lookup_uri_with_webfinger(
            self.session, f"acct:{self.username}@{self.domain}", f"http://{self.domain}"
        )
        return actor_uri

    async def determine_actor_firefish_id(self):
        """Determines the firefish id for the user on the
        one_actor server, i.e. the one with hostname
        `pasture_one_actor"""
        response = await self.session.post(
            f"http://{self.domain}/api/users/search", data={"query": "actor"}
        )
        users = await response.json()

        for user in users:
            if user.get("host") == "pasture_one_actor":
                return user.get("id")

    async def user_post_with_published(self, published: datetime):
        if not self.firefish_id:
            self.firefish_id = await self.determine_actor_firefish_id()

        response = await self.session.post(
            f"http://{self.domain}/api/users/notes",
            data={"userId": self.firefish_id},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        notes = await response.json()

        for data in notes:
            created_at = data.get("createdAt")
            created_at = datetime.fromisoformat(created_at.removesuffix("Z"))
            if created_at == published:
                return data

        return None

    async def top_public(self):
        response = await self.session.post(
            f"http://{self.domain}/api/notes/global-timeline"
        )
        public_timeline = await response.json()
        return public_timeline[0]

    async def top_public_with_published(self, published: datetime) -> dict | None:
        data = await self.top_public()
        created_at = data.get("createdAt")
        created_at = datetime.fromisoformat(created_at.removesuffix("Z"))
        if created_at == published:
            return data
        return None

    async def last_activity(
        self, session: aiohttp.ClientSession
    ) -> ApplicationAdapterForLastActivity:
        self.session = session

        actor_uri = await self.determine_actor_uri()

        return ApplicationAdapterForLastActivity(
            actor_uri=actor_uri,
            fetch_activity=self.user_post_with_published,
            application_name="firefish",
        )
