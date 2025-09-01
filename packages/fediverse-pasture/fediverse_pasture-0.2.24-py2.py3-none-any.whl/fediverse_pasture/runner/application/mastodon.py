# SPDX-FileCopyrightText: 2023-2024 Helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
import logging
import json
import aiohttp

from bovine.clients.bearer import BearerAuthClient

from fediverse_pasture.types import ApplicationAdapterForLastActivity

logger = logging.getLogger(__name__)


@dataclass
class MastodonApplication:
    domain: str
    access_token: str
    username: str
    client: BearerAuthClient | None = None
    actor_uri: str | None = None

    def determine_actor_uri(self):
        if self.actor_uri:
            return self.actor_uri
        return f"http://{self.domain}/users/{self.username}"

    async def public_items(self):
        response = await self.client.get(
            f"http://{self.domain}/api/v1/timelines/public"
        )
        public_timeline = await response.json()
        logger.debug(json.dumps(public_timeline, indent=2))

        return public_timeline

    async def top_public_with_object_id(self, object_id: str) -> dict | None:
        for item in await self.public_items():
            if object_id in json.dumps(item):
                return item

        return None

    def last_activity(
        self, session: aiohttp.ClientSession, application_name: str = "mastodon"
    ) -> ApplicationAdapterForLastActivity:
        self.client = BearerAuthClient(session, self.access_token)

        return ApplicationAdapterForLastActivity(
            actor_uri=self.determine_actor_uri(),
            fetch_activity=self.top_public_with_object_id,
            application_name=application_name,
        )
