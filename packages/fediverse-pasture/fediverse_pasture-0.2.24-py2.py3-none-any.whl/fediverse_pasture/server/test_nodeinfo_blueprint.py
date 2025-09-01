import pytest

from quart import Quart

from .nodeinfo_blueprint import nodeinfo_blueprint


@pytest.fixture
def app_client():
    app = Quart(__name__)
    app.register_blueprint(nodeinfo_blueprint)

    yield app.test_client()


async def test_url(app_client):
    response = await app_client.get("/.well-known/nodeinfo")

    assert response.status_code == 200

    data = await response.json

    assert data["links"][0]["href"] == "http://localhost/.well-known/nodeinfo2_0"
