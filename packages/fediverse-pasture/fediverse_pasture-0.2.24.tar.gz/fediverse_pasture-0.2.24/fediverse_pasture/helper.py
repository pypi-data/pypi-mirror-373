# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from contextlib import asynccontextmanager

from fediverse_pasture.runner import (
    ActivitySender,
    ActivityRunner,
)
from fediverse_pasture.runner.application import app_name_to_coroutine
from fediverse_pasture.one_actor import bovine_actor_and_session


@asynccontextmanager
async def activity_runner(
    application_name: str,
):
    application_generator = app_name_to_coroutine.get(application_name)

    if application_generator is None:
        available_applications = ", ".join(app_name_to_coroutine.keys())
        raise ValueError(
            f"Unknown application '{application_name}' available applications are {available_applications}"
        )

    async with bovine_actor_and_session() as (bovine_actor, actor, session):
        sender = ActivitySender.for_actor(bovine_actor, actor)

        application = await application_generator(session)

        activity_runner = ActivityRunner(sender, [application])

        yield activity_runner
