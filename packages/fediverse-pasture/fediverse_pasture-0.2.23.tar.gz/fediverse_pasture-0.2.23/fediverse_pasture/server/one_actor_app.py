import asyncio
import json

from quart import Quart, make_response
from . import BlueprintForActors

import logging

logger = logging.getLogger(__name__)


def app_for_data_provider(data_provider):
    app = Quart(__name__)
    queue = asyncio.Queue()

    async def generator():
        yield """<html><body><h1>Inbox content</h1>\n"""
        while True:
            data = await queue.get()
            if data:
                yield f"""<p><pre>{json.dumps(data, indent=2)}</pre></p>\n"""

    async def on_inbox(data):
        logger.error(data)
        await queue.put(data)

    app.register_blueprint(
        BlueprintForActors(
            actors=[data_provider.one_actor], on_inbox=on_inbox
        ).blueprint
    )

    @app.get("/")
    async def inbox_display():
        response = await make_response(generator())
        response.timeout = None
        return response

    return app
