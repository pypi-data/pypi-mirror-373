# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock
from contextlib import asynccontextmanager
from fediverse_pasture.types import ApplicationAdapterForActor

from .verify_actor import VerifyActorRunner, format_verify_actor_result


async def test_verify_actor():
    session = AsyncMock()
    runner = VerifyActorRunner(
        application=ApplicationAdapterForActor(
            actor_uri="about:actor", application_name="name"
        ),
        session=session,
    )

    @asynccontextmanager
    async def post_response(*args, **kwargs):
        response = AsyncMock()
        response.json.return_value = {"result": "result", "messages": "messages"}
        yield response

    session.post = post_response

    result = await runner.run()

    assert result == {
        "verify_actor_table": "result",
        "messages": "messages",
        "application_name": "name",
    }


def test_format():
    entry_data = {
        "alice": {"get_actor": False, "post_inbox": False},
        "bob": {"get_actor": True, "post_inbox": True},
        "claire": {"get_actor": True, "post_inbox": True},
        "dean": {"get_actor": False, "post_inbox": False},
        "emily": {"get_actor": True, "post_inbox": True},
        "frank": {"get_actor": True, "post_inbox": True},
    }

    result = [
        {
            "application_name": "test",
            "verify_actor_table": entry_data,
            "messages": "bla",
        }
    ]

    markdown = format_verify_actor_result(result)

    print()
    print()
    print(markdown)
