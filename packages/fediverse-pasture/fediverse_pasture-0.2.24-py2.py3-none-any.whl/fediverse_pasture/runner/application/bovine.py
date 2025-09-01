# SPDX-FileCopyrightText: 2023, 2024 Helge
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass
from datetime import datetime
import logging
import aiohttp

from bovine import BovineClient

from fediverse_pasture.types import ApplicationAdapterForLastActivity

logger = logging.getLogger(__name__)


@dataclass
class BovineApplication:
    domain: str
    username: str
    secret: str
    actor_uri: str | None = None
    client: BovineClient | None = None

    async def fetch_activity(self, published):
        try:
            inbox = self.client.inbox()

            result = await inbox.__anext__()
            parsed_published = datetime.fromisoformat(
                result["object"]["published"].removesuffix("Z")
            )
            if parsed_published == published:
                return result.get("object")
        except Exception as e:
            print("Something went wrong with", repr(e))
        return None

    async def last_activity(
        self, session: aiohttp.ClientSession
    ) -> ApplicationAdapterForLastActivity:
        self.client = BovineClient(
            domain=f"http://{self.domain}",
            secret=self.secret,
        )
        await self.client.init(session=session)

        return ApplicationAdapterForLastActivity(
            actor_uri=self.client.actor_id,
            fetch_activity=self.fetch_activity,
            application_name=self.domain,
        )
