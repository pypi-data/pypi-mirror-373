# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from .runner import ActivityRunner

from .helper import activity_runner


@pytest.mark.skip("Currently requires data.toml to exist")
async def test_activity_runner():
    async with activity_runner("mastodon") as runner:
        assert isinstance(runner, ActivityRunner)
