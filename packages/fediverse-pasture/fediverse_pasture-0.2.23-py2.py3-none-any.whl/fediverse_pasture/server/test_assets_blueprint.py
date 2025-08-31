# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from quart import Quart

from . import assets_blueprint_for_directory


@pytest.fixture
def test_client():
    app = Quart(__name__)
    app.register_blueprint(assets_blueprint_for_directory("assets"))

    yield app.test_client()


async def test_not_found(test_client):
    response = await test_client.get("/assets/unknown")
    assert response.status_code == 404


async def test_json(test_client):
    response = await test_client.get("/assets/test.json")

    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/json"


async def test_activitypub(test_client):
    response = await test_client.get("/assets/test.jsonap")

    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/activity+json"
