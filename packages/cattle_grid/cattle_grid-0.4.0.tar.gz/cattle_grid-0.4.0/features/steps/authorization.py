import logging

from behave import when, then
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from bovine.activitystreams import factories_for_actor_object

from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.activity_pub.actor.requester import is_valid_requester

from cattle_grid.dependencies.globals import global_container

logger = logging.getLogger(__name__)


@when('"{alice}" creates an object addressed to "{recipient}"')
def object_addressed_to(context, alice, recipient):
    alice_actor = context.actors[alice]
    _, object_factory = factories_for_actor_object(alice_actor)

    if recipient == "public":
        context.object = object_factory.note(content="moo").as_public().build()
    elif recipient == "followers":
        context.object = object_factory.note(content="moo").as_followers().build()
    else:
        context.object = object_factory.note(
            content="moo", to={context.actors[recipient].get("id")}
        ).build()


@then('"{bob}" is "{state}" to view this object')
async def check_allowed(context, bob, state):
    bob_id = context.actors[bob].get("id")

    async with global_container.alchemy_database() as engine:
        async with async_sessionmaker(engine)() as session:
            alice = await session.scalar(
                select(Actor).where(
                    Actor.actor_id == context.object.get("attributedTo")
                )
            )
            assert alice
            is_valid = await is_valid_requester(session, bob_id, alice, context.object)

    if is_valid:
        assert state == "authorized"
    else:
        assert state == "unauthorized"
