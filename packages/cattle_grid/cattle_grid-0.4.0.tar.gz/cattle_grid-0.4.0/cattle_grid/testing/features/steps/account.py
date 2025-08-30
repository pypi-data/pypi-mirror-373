import os

import asyncio
import logging

from behave import given, when, then

from almabtrieb import Almabtrieb

from cattle_grid.config import load_settings
from cattle_grid.account.account import create_account, add_permission
from cattle_grid.testing.features import publish_as
from cattle_grid.database import database_session

logger = logging.getLogger(__name__)


@given('An account called "{alice}"')
async def create_account_step(context, alice):
    config = load_settings()
    async with database_session(db_uri=config.get("db_uri")) as session:
        account = await create_account(session, alice, alice)
        assert account
        await add_permission(session, account, "admin")

    mq_host = os.environ.get("CATTLE_GRID_MQ", "rabbitmq")

    context.connections[alice] = Almabtrieb.from_connection_string(
        f"amqp://{alice}:{alice}@{mq_host}/", silent=True
    )
    context.connections[alice].task = asyncio.create_task(
        context.connections[alice].run()
    )

    for _ in range(10):
        if context.connections[alice].connected:
            return
        logger.debug("Connecting")
        await asyncio.sleep(0.1)

    raise RuntimeError("Could not connect")


@given('"{alice}" created an actor called "{alyssa}"')
def create_actor_step(context, alice, alyssa):
    hostname = {"alice": "abel", "bob": "banach", "Bob": "banach"}.get(alyssa, "abel")

    context.execute_steps(
        f"""
        Given "{alice}" created an actor on "{hostname}" called "{alyssa}"
        """
    )


@given('"{alice}" created an actor on "{hostname}" called "{alyssa}"')
async def create_actor_on_host_step(context, alice, alyssa, hostname):
    result = await context.connections[alice].create_actor(
        base_url=f"http://{hostname}", preferred_username=alyssa
    )
    context.actors[alyssa] = result


@when('"{alice}" deletes the actor "{alyssa}"')
async def alice_delete_actor_step(context, alice, alyssa):
    alyssa_id = context.actors[alyssa].get("id")

    await publish_as(
        context,
        alice,
        "delete_actor",
        {
            "actor": alyssa_id,
        },
    )


@then('"{alice}" has no actors')
async def check_no_actors(context, alice):
    response = await context.connections[alice].info()

    assert len(response.actors) == 0, f"Alice has actors {', '.join(response.actors)}"
