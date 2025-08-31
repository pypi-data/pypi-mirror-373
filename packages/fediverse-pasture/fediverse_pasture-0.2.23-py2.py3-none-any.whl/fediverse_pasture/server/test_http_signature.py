# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from quart import Quart

import pytest
from .http_signature import http_signature_blueprint


@pytest.fixture
async def test_client():
    app = Quart(__name__)
    app.register_blueprint(http_signature_blueprint)
    yield app.test_client()


async def test_get_no_signature(test_client):
    response = await test_client.get("/")

    assert response.status_code == 401

    result = await response.get_json()

    assert result["x error"] == "Signature header is missing"


async def test_post_with_signature(test_client):
    response = await test_client.post(
        "/",
        data="{}",
        headers={
            "signature": 'keyId="about:inline",headers=" host date",signature="1xx=="'
        },
    )

    assert response.status_code == 401
