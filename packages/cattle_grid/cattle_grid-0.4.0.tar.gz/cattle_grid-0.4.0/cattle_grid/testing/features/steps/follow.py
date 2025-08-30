import logging

from behave import when, given

from uuid import uuid4

from bovine.activitystreams import factories_for_actor_object

from cattle_grid.testing.features import publish_as, send_message_as_actor

logger = logging.getLogger(__name__)


@when('"{alice}" sends "{bob}" a Follow Activity')
async def send_follow(context, alice, bob):
    """Sends a follow Activity. Usage

    ```gherkin
    When "Alice" sends "Bob" a Follow Activity
    ```

    Stores the follow activity in `context.follow_activity`
    """
    alice_actor = context.actors[alice]
    bob_id = context.actors[bob].get("id")
    activity_factory, _ = factories_for_actor_object(alice_actor)

    context.follow_id = "follow:" + str(uuid4())

    context.follow_activity = activity_factory.follow(
        bob_id, id=context.follow_id
    ).build()

    await publish_as(
        context,
        alice,
        "send_message",
        send_message_as_actor(alice_actor, context.follow_activity),
    )


@when('"{actor}" sends an Accept to this Follow Activity')
async def accept_follow_request(context, actor):
    """Checks that Alice received a follow Activity and then
    accepts this follow activity

    ```gherkin
    When "Alice" sends an Accept to this Follow Activity
    ```
    """
    result = await context.connections[actor].next_incoming()
    received_activity = result.get("data")
    if "raw" in received_activity:
        received_activity = received_activity["raw"]

    logger.debug("Got follow request:")
    logger.debug(received_activity)

    assert received_activity["type"] == "Follow"

    follow_id = received_activity["id"]
    to_follow = received_activity["actor"]

    alice = context.actors[actor]
    activity_factory, _ = factories_for_actor_object(alice)

    activity = activity_factory.accept(follow_id, to={to_follow}).build()
    activity["id"] = "accept:" + str(uuid4())

    await publish_as(
        context, actor, "send_message", send_message_as_actor(alice, activity)
    )


@given('"{bob}" follows "{alice}"')
def actor_follows_other(context, bob, alice):
    """Combination of two steps, i.e.

    ```gherkin
    When "Alice" follows "Bob"
    ```

    is the same as

    ```gherkin
    When "Alice" sends "Bob" a Follow Activity
    And "Bob" sends an Accept to this Follow Activity
    ```
    """

    logger.debug("Available conections %s", ", ".join(context.connections.keys()))

    if alice not in context.connections:
        context.execute_steps(
            f"""
        When "{bob}" sends "{alice}" a Follow Activity
    """
        )
    else:
        context.execute_steps(
            f"""
        When "{bob}" sends "{alice}" a Follow Activity
        And "{alice}" sends an Accept to this Follow Activity
    """
        )


@when('"{bob}" sends "{alice}" an Undo Follow Activity')
async def send_undo_follow(context, bob, alice):
    """Sends an Undo Follow activity for the follow activity
    with id stored in `context.follow_activity`.

    Usage:

    ```gherkin
    When "Bob" sends "Alice" an Undo Follow Activity
    ```
    """
    actor = context.actors[bob]
    activity_factory, _ = factories_for_actor_object(actor)

    activity = activity_factory.undo(context.follow_activity).build()
    if isinstance(activity["object"], dict):
        activity["object"] = activity["object"]["id"]

    activity["id"] = "undo:" + str(uuid4())

    await publish_as(
        context, bob, "send_message", send_message_as_actor(actor, activity)
    )


@given('"{alice}" automatically accepts followers')
async def automatically_accept_followers(context, alice):
    """FIXME: Should toggle"""

    actor = context.actors[alice]

    await publish_as(
        context,
        alice,
        "update_actor",
        {"actor": actor.get("id"), "autoFollow": True},
    )


@when('"{alice}" sends "{bob}" a Reject Follow Activity')
async def send_reject_follow(context, alice, bob):
    """Sends an Undo Follow activity for the follow activity
    with id stored in `context.follow_activity`.

    Usage:

    ```gherkin
    When "Alice" sends "Bob" a Reject Follow Activity
    ```
    """
    actor = context.actors[alice]
    activity_factory, _ = factories_for_actor_object(actor)

    activity = activity_factory.reject(context.follow_activity).build()
    if isinstance(activity["object"], dict):
        activity["object"] = activity["object"]["id"]

    activity["id"] = "reject:" + str(uuid4())

    await publish_as(
        context, alice, "send_message", send_message_as_actor(actor, activity)
    )
