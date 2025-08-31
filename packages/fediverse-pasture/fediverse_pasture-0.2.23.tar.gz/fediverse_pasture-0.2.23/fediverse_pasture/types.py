# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Class to track messages"""

    steps: List[str] = field(
        default_factory=list, metadata={"description": "a log of strings"}
    )

    def add(self, msg):
        """Adds a message to steps and logs it to info"""
        logger.info(msg)
        self.steps.append(msg)

    def error(self, msg):
        """Logs an error and returns a message object"""
        logger.error(msg)
        return {"x error": msg, **self.response}

    @property
    def response(self):
        """Returns a dictionary with a single key "steps" containing the steps"""
        return {"steps": self.steps}


@dataclass
class ApplicationAdapterForLastActivity:
    """Basic type that is used to describe how to interact with
    an external application. actor_uri represents the actor
    a message will be sent to. fetch_activity is used to
    fetch this activity.
    """

    actor_uri: str = field(metadata={"description": "The actor uri"})
    application_name: str = field(
        metadata={"description": "The name the application will be displayed as"}
    )
    fetch_activity: Callable[[datetime], Awaitable[dict | None]] = field(
        metadata={
            "description": "coroutine that retrieves the activity with a specified published date."
        }
    )


@dataclass
class ApplicationAdapterForActor:
    """Basic type that is used to describe how to interact with
    an external application. actor_uri represents the actor
    a message will be sent to.
    """

    actor_uri: str = field(metadata={"description": "The actor uri"})
    application_name: str = field(
        metadata={"description": "The name the application will be displayed as"}
    )


MessageModifier = Callable[[dict], dict]
"""Used to add the variable content to an activity pub message. The intended usage can be seen in the
[ActivitySender.init_create_note][fediverse_pasture.runner.ActivitySender.init_create_note] method.
"""
