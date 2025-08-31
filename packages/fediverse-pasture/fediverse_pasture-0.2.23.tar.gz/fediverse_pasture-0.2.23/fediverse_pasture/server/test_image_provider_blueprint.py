# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest
from quart import Quart

from .image_provider_blueprint import image_provider_blueprint


@pytest.fixture
async def image_test_client():
    app = Quart(__name__)
    app.register_blueprint(image_provider_blueprint)

    yield app.test_client()


async def test_can_get_image_at_url(image_test_client):
    response = await image_test_client.get("/aaa111")

    assert response.status_code == 200
