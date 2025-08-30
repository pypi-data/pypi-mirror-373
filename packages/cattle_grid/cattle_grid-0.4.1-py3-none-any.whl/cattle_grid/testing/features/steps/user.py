import logging
from behave import given, when

from cattle_grid.model.exchange import UpdateActorMessage

from cattle_grid.testing.features import publish_as

logger = logging.getLogger(__name__)


@given('A new user called "{username}" on "{hostname}"')
def new_user_on_server(context, username, hostname):
    context.execute_steps(
        f"""
        Given An account called "{username}"
        Given "{username}" created an actor on "{hostname}" called "{username}"
        """
    )


@given('A new user called "{username}"')
def new_user(context, username):
    """Creates a new user

    Usage example:

    ```gherkin
    Given A new user called "Alice"
    ```
    """
    hostname = {"alice": "abel", "bob": "banach", "Bob": "banach"}.get(username, "abel")

    context.execute_steps(
        f"""
        Given A new user called "{username}" on "{hostname}"
        """
    )


@when('"{alice}" updates her profile')
async def update_profile(context, alice):
    """
    ```gherkin
    When "Alice" updates her profile
    ```
    """

    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_id = context.actors[alice].get("id")

    msg = UpdateActorMessage(
        actor=alice_id, profile={"summary": "I love cows"}
    ).model_dump()

    await publish_as(context, alice, "update_actor", msg)


@when('"{alice}" deletes herself')
@when('"{alice}" deletes himself')
async def actor_deletes_themselves(context, alice):
    """
    ```gherkin
    When "Alice" deletes herself
    When "Bob" deletes himself
    ```
    """
    alice_id = context.actors[alice].get("id")

    await publish_as(
        context,
        alice,
        "delete_actor",
        {
            "actor": alice_id,
        },
    )
