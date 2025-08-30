import json
from behave import when, then
from almabtrieb import NoIncomingException
from bovine.activitystreams import factories_for_actor_object

from cattle_grid.testing.features import (
    publish_as,
    id_generator_for_actor,
    fetch_request,
    send_message_as_actor,
)


@when('"{actor}" sends "{target}" a message saying "{text}"')
async def send_message(context, actor, target, text):
    """Used to send a message. The message has the format (with a lot of stuff omitted)

    ```json
    {
        "type": "Create",
        "object": {
            "type": "Note",
            "content": text,
            "to": [actor_id_of_target]
        }
    }
    ```

    This step can be used as

    ```gherkin
    When "alice" sends "bob" a message saying "You stole my milk!"
    ```
    """
    alice = context.actors[actor]
    activity_factory, object_factory = factories_for_actor_object(
        alice, id_generator=id_generator_for_actor(alice)
    )

    bob_id = context.actors[target].get("id")

    note = object_factory.note(content=text, to={bob_id}).build()
    activity = activity_factory.create(note).build()

    await publish_as(
        context,
        actor,
        "send_message",
        send_message_as_actor(alice, activity),
    )


@then('"{actor}" receives an activity')
async def receive_activity(context, actor):
    """Ensures that an incoming activity was received
    and stores it in `context.activity`.

    ```gherkin
    Then "bob" receives an activity
    ```
    """

    data = await context.connections[actor].next_incoming()
    assert data.get("event_type") == "incoming"

    context.activity = data["data"]["raw"]

    assert context.activity["@context"]


@then('"{actor}" does not receive an activity')
async def not_receive_activity(context, actor):
    """Ensures that no incoming activity was received

    ```gherkin
    Then "bob" does not receive an activity
    ```
    """

    try:
        result = await context.connections[actor].next_incoming()

        assert result is None, f"Received activity {json.dumps(result, indent=2)}"
    except NoIncomingException:
        ...


@then('the received activity is of type "{activity_type}"')
def check_activity_type(context, activity_type):
    """Checks that the received activity from [cattle_grid.testing.features.steps.messaging.receive_activity][]
    is of type `activity_type`.

    ```gherkin
    Then the received activity is of type "Update"
    ```
    """

    received = context.activity
    if "raw" in received:
        received = received["raw"]

    import json

    print(json.dumps(received, indent=2))

    assert received.get("type") == activity_type, (
        f"Activity {received} has the wrong type"
    )


@then('"{actor}" receives a message saying "{text}"')
async def check_message(context, actor, text):
    """Used to check if the last message received by actor
    is saying the correct thing.

    ```gherkin
    Then "bob" receives a message saying "Got milk?"
    ```
    """

    data = await context.connections[actor].next_incoming()

    assert data.get("event_type") == "incoming"
    activity = data.get("data")

    if "raw" in activity:
        activity = activity["raw"]

    assert activity.get("type") == "Create", f"got {activity}"
    assert activity.get("@context"), f"got {activity}"

    obj = activity.get("object", {})
    assert obj.get("content") == text, f"""got {obj.get("content")}"""

    context.received_object = obj


@then('"{bob}" can lookup this message by id')
async def check_lookup_message(context, bob):
    obj_id = context.received_object.get("id")

    result = await fetch_request(context, bob, obj_id)

    assert isinstance(result, dict), f"got {result}"
    assert result == context.received_object, result


@when('"{actor}" messages her followers "{text}"')
async def send_message_followers(context, actor, text):
    """Used to send a message to the followers. The message has the format (with a lot of stuff omitted)

    ```json
    {
        "type": "Create",
        "object": {
            "type": "Note",
            "content": text,
            "to": [followers_collection_of_actor]
        }
    }
    ```

    This step can be used as

    ```gherkin
    When "alice" messages her followers "Got milk?"
    ```
    """
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice = context.actors[actor]

    activity_factory, object_factory = factories_for_actor_object(
        alice, id_generator=id_generator_for_actor(alice)
    )
    note = object_factory.note(content=text).as_followers().build()
    activity = activity_factory.create(note).build()

    await publish_as(
        context,
        actor,
        "send_message",
        send_message_as_actor(alice, activity),
    )
