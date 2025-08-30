from behave import when, then

from bovine.activitystreams import factories_for_actor_object

from cattle_grid.testing.features import publish_as, fetch_request


@when('"{alice}" publishes a "{moo}" animal sound to her follows')
async def send_sound(context, alice, moo):
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_actor = context.actors[alice]
    activity_factory, _ = factories_for_actor_object(alice_actor)

    activity = (
        activity_factory.custom(type="AnimalSound", content="moo").as_public().build()
    )

    await publish_as(
        context,
        alice,
        "publish_activity",
        {"actor": context.actors[alice].get("id"), "data": activity},
    )


@then('"{bob}" can retrieve the activity')
async def can_retrieve_activity(context, bob):
    result = await fetch_request(context, bob, context.activity.get("id"))
    assert result
