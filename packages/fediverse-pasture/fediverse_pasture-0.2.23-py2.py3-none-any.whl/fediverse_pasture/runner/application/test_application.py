# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from unittest.mock import patch

from . import activity_for_mastodon, activity_for_firefish

from fediverse_pasture.types import ApplicationAdapterForLastActivity


async def test_activity_for_mastodon():
    result = await activity_for_mastodon("domain", "user", "xxx", "session")

    assert isinstance(result, ApplicationAdapterForLastActivity)


@patch("bovine.clients.lookup_uri_with_webfinger")
async def test_activity_for_firefish(mock_lookup):
    mock_lookup.return_value = "actor_uri", 0
    result = await activity_for_firefish("domain", "user", "session")

    assert isinstance(result, ApplicationAdapterForLastActivity)

    assert result.actor_uri == "actor_uri"
