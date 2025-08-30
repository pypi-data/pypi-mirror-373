from behave import given, then
from cattle_grid.model.exchange import (
    UpdateActorMessage,
    UpdateActionType,
    UpdateIdentifierAction,
)
from cattle_grid.testing.features import publish_as


@given('"{alice}" adds "{identifier}" as a primary identifier')
async def add_identifier(context, alice, identifier):
    actor = context.actors[alice]

    msg = UpdateActorMessage(
        actor=actor.get("id"),
        actions=[
            UpdateIdentifierAction(
                action=UpdateActionType.create_identifier,
                identifier=identifier,
                primary=True,
            )
        ],
    ).model_dump()

    await publish_as(context, alice, "update_actor", msg)


@then('The preferred username is "{alex}"')
def check_preferred_username(context, alex):
    assert context.result.get("preferredUsername") == alex


@then('"{identifier}" is contained in the identifiers array')
def check_identifiers(context, identifier):
    assert identifier in context.result.get("identifiers")


@then('"{identifier}" is not contained in the identifiers array')
def check_not_in_identifiers(context, identifier):
    assert identifier not in context.result.get("identifiers")
