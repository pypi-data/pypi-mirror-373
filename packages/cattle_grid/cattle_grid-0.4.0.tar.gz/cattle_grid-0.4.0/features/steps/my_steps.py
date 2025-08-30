import logging

from behave import then, when

from bovine.clients import lookup_uri_with_webfinger

from cattle_grid.testing.features import fetch_request

logger = logging.getLogger(__name__)


@when('One queries webfinger for "{resource}"')
async def query_webfinger(context, resource):
    context.actor_uri, _ = await lookup_uri_with_webfinger(
        context.session, resource, domain="http://abel"
    )


@then('The actor URI of "{username}" is returned')
def result_is_actor_uri(context, username):
    assert context.actor_uri == context.actors[username]["id"]


@then("No actor URI is returned")
def no_actor_uri_result(context):
    assert context.actor_uri is None, (
        f"Actor URI is {context.actor_uri}; should be None"
    )


@when('"{bob}" looks up the actor id of "{alice}"')
async def bob_looks_up_alice(context, bob, alice):
    context.lookup_result = await fetch_request(
        context, bob, context.actors[alice].get("id")
    )


@then("410 gone is returned")
def gone_returned(context):
    logger.info(context.lookup_result)
    assert context.lookup_result["type"] == "Tombstone"

    # FIXME: This is not what I want. Requires bovine
    # to return appropriate information


@then('"{bob}" can fetch this activity')
async def can_fetch_Activity(context, bob):
    activity_id = context.activity.get("id")

    result = await fetch_request(context, bob, activity_id)

    assert result
    assert result.get("type") == "Update"
