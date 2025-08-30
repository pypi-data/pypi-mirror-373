from uuid import uuid4
from behave import when, given

from bovine.activitystreams import factories_for_actor_object


from cattle_grid.testing.features import (
    publish_as,
    id_generator_for_actor,
    send_message_as_actor,
)


@given('"{alice}" blocks "{bob}"')
@when('"{alice}" blocks "{bob}"')
async def send_block(context, alice, bob):
    """
    ```gherkin
    When "Alice" blocks "Bob"
    ```

    The id of the block is stored in `context.block_id`
    """

    actor = context.actors[alice]
    activity_factory, object_factory = factories_for_actor_object(
        actor, id_generator=id_generator_for_actor(actor)
    )

    bob_id = context.actors[bob].get("id")

    activity = activity_factory.custom(type="Block", object=bob_id, to={bob_id}).build()

    context.block_id = activity.get("id")

    await publish_as(
        context,
        alice,
        "send_message",
        send_message_as_actor(actor, activity),
    )


@when('"{bob}" unblocks "{alice}"')
async def unblock(context, bob, alice):
    """Sends an Undo Block activity for
    the id stored in `context.block_id`.

    Usage:

    ```gherkin
    When "Bob" unblocks "Alice"
    ```
    """
    actor = context.actors[bob]
    activity_factory, _ = factories_for_actor_object(actor)
    alice_id = context.actors[alice].get("id")

    activity = activity_factory.custom(
        object=context.block_id, to={alice_id}, type="Undo"
    ).build()
    activity["id"] = "undo:" + str(uuid4())

    await publish_as(
        context,
        bob,
        "send_message",
        send_message_as_actor(actor, activity),
    )
