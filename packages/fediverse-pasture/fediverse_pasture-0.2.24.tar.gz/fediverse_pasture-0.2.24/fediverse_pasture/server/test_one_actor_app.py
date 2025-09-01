import pytest
import asyncio
from .one_actor_app import app_for_data_provider

from fediverse_pasture.data_provider import DataProvider


@pytest.fixture
def client_one_actor():
    dp = DataProvider.generate(with_possible_actors=False)
    app = app_for_data_provider(dp)

    yield app.test_client()


async def test_inbox_display_no_content(client_one_actor):
    async with client_one_actor.request("/") as connection:
        data = await connection.receive()

        assert "Inbox content" in data.decode()
        assert "\n" in data.decode()

        await connection.disconnect()


async def test_inbox_display(client_one_actor):
    async with client_one_actor.request("/") as connection:
        data = await connection.receive()

        assert "Inbox content" in data.decode()
        await connection.disconnect()

    response = await client_one_actor.post("/actor/inbox", json={"test": "find me"})

    assert response.status_code == 202

    await asyncio.sleep(0.1)

    async with client_one_actor.request("/") as connection:
        data = await connection.receive()
        assert "Inbox content" in data.decode()
        data = await connection.receive()
        assert "find me" in data.decode()

        await connection.disconnect()
