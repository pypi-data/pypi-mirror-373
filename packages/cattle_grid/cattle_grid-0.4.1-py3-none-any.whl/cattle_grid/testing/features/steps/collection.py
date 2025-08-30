import logging

from behave import then

from cattle_grid.testing.features import fetch_request

logger = logging.getLogger(__name__)


@then('The "{collection}" collection of "{bob}" does not include "{alice}"')
async def check_collection(context, alice, bob, collection):
    """Used to check if the followers or following collection
    of the actor `bob` does not contain the actor `alice`.

    ```gherkin
    Then The "followers" collection of "bob" does not include "alice"
    ```
    """
    result = await fetch_request(
        context,
        bob,
        context.actors[bob].get(collection),
    )

    assert result

    actor = context.actors[alice].get("id")

    if "raw" in result:
        result = result["raw"]

    assert result.get("type") == "OrderedCollection"
    assert actor not in result.get("orderedItems", [])


@then('The "{collection}" collection of "{bob}" contains "{alice}"')
async def check_collection_contains(context, alice, bob, collection):
    """Used to check if the followers or following collection
    of the actor `bob` contains the actor `alice`.

    ```gherkin
    Then The "followers" collection of "bob" contains "alice"
    ```
    """
    result = await fetch_request(
        context,
        bob,
        context.actors[bob].get(collection),
    )

    bob_id = context.actors[alice].get("id")

    if "raw" in result:
        result = result["raw"]

    assert result.get("type") == "OrderedCollection"
    assert bob_id in result.get("orderedItems", [])
