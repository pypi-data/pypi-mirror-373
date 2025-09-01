# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import AsyncMock, MagicMock

from . import ActivityRunner


async def test_run_for_modifier():
    app = AsyncMock(actor_uri="https://actor.example/uri", application_name="app")
    sender = AsyncMock(init_create_note=MagicMock())

    app.fetch_activity = AsyncMock(return_value="test")

    runner = ActivityRunner(activity_sender=sender, applications=[app], wait_time=0.1)

    result = await runner.run_for_modifier(lambda x: x)

    app.fetch_activity.assert_awaited_once()

    assert result["app"] == "test"


async def test_run_for_modifier_with_sequence():
    app = AsyncMock(actor_uri="https://actor.example/uri", application_name="app")
    sender = AsyncMock(init_create_note=MagicMock())

    app.fetch_activity = AsyncMock(side_effect=[None, "test"])

    runner = ActivityRunner(activity_sender=sender, applications=[app], wait_time=0.1)

    result = await runner.run_for_modifier(lambda x: x)

    assert result["app"] == "test"
