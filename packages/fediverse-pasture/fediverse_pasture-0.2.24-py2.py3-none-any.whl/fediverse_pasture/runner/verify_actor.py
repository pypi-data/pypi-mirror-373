# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
import textwrap
from dataclasses import dataclass
from fediverse_pasture.types import ApplicationAdapterForActor


@dataclass
class VerifyActorRunner:
    """Class to run query the verify runner application for
    various applications"""

    application: ApplicationAdapterForActor
    verify_actor_url: str = "http://pasture_verify_actor/"
    session: aiohttp.ClientSession | None = None

    async def run(self) -> list:
        """Runs the query. Returns a list containing the results
        for each application"""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                return await self.run_for_session(session)

        return await self.run_for_session(self.session)

    async def run_for_session(self, session) -> dict:
        async with session.post(
            self.verify_actor_url,
            data=aiohttp.FormData({"actor_uri": self.application.actor_uri}),
            headers={
                "content_type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
        ) as response:
            data = await response.json()
            return {
                "application_name": self.application.application_name,
                "verify_actor_table": data["result"],
                "messages": data["messages"],
            }


def x_or_not(value):
    if value:
        return "X"
    return " "


def format_verify_actor_result(result, prefix="###"):
    """Routine to convert the obtained result into a markdown string"""
    lines = []
    lines.append(f"{prefix} Verify Actor")
    lines.append("")
    for entry in result:
        lines.append(f'''=== "{entry["application_name"]}"''')
        lines.append("")
        table = [
            ("| Name   | GET Actor | POST Inbox |"),
            ("| ------ | --------- | ---------- |"),
        ]
        for name, value in entry["verify_actor_table"].items():
            if name != "webfinger":
                x_get = x_or_not(value["get_actor"])
                x_post = x_or_not(value["post_inbox"])
                table.append(f"""| {name} | {x_get} | {x_post} |""")

        lines.append(textwrap.indent("\n".join(table), " " * 4))
        lines.append("")

    lines.append("")
    lines.append(f"{prefix} Messages")
    lines.append("")
    for entry in result:
        lines.append(f'''=== "{entry["application_name"]}"''')
        lines.append("")
        lines.append("    ```json")
        lines.append(textwrap.indent(entry["messages"], " " * 4))
        lines.append("    ```")
        lines.append("")

    return "\n".join(lines)
