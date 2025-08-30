"""The before_all, _scenario, and after_scenario functions
need to be imported in your environment.py file, e.g.


```python title="features/environment.py"
--8<-- "./features/environment.py"
```
"""

import asyncio
import aiohttp
import secrets
import logging

from almabtrieb.exceptions import ErrorMessageException

from cattle_grid.config import load_settings
from cattle_grid.account.account import delete_account
from cattle_grid.database import database_session
from .reporting import publish_reporting

logger = logging.getLogger(__name__)


def id_generator_for_actor(actor):
    def gen():
        return actor.get("id") + "/" + secrets.token_hex(8)

    return gen


async def create_session(context):
    if not context.session:
        context.session = aiohttp.ClientSession()


async def close_session(context):
    config = load_settings()

    async with database_session(db_uri=config.db_uri) as session:  # type: ignore
        for name, connection in context.connections.items():
            try:
                if name in context.actors:
                    await connection.trigger(
                        "delete_actor",
                        {
                            "actor": context.actors[name].get("id"),
                        },
                    )
                    await asyncio.sleep(0.1)

                await delete_account(session, name, name)
            except Exception as e:
                logger.exception(e)

    await context.session.close()

    try:
        for connection in context.connections.values():
            connection.task.cancel()
            try:
                await connection.task
            except asyncio.CancelledError:
                pass
    except Exception as e:
        logger.exception(e)


def before_all(context):
    """Called in features/environment.py"""
    tortoise_logger = logging.getLogger("tortoise")
    tortoise_logger.setLevel(logging.WARNING)
    context.session = None

    context.actors = {}
    context.connections = {}


def before_scenario(context, scenario):
    """Called in features/environment.py"""
    asyncio.get_event_loop().run_until_complete(create_session(context))

    context.actors = {}
    context.connections = {}

    asyncio.get_event_loop().run_until_complete(
        publish_reporting(
            "scenario",
            {
                "name": scenario.name,
                "file": scenario.filename,
                "description": scenario.description,
            },
        )
    )


def after_scenario(context, scenario):
    """Called in features/environment.py"""

    asyncio.get_event_loop().run_until_complete(
        publish_reporting(
            "scenario_end",
            {},
        )
    )

    if context.session:
        asyncio.get_event_loop().run_until_complete(close_session(context))
        context.session = None


async def publish_as(
    context, username: str, method: str, data: dict, timeout: float = 0.3
):
    """Publishes a message through the gateway

    :param data: The message to be published"""
    connection = context.connections[username]

    await connection.trigger(method, data)
    await asyncio.sleep(timeout)


async def fetch_request(context, username: str, uri: str) -> dict | None:
    """Sends a fetch request for the uri through the gateway

    :param context: The behave context
    :param username: username performing the result
    :param uri: URI being looked up
    :return:
    """
    connection = context.connections[username]
    actor = context.actors[username].get("id")

    await asyncio.sleep(0.1)

    try:
        data = await connection.fetch(actor, uri)

        assert data.uri == uri

        return data.data
    except ErrorMessageException:
        return None


def send_message_as_actor(actor, activity):
    return {"actor": actor.get("id"), "data": activity}
