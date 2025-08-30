from behave import then, when, given
from cattle_grid.testing.features import publish_as


@given('"{alice}" has the PropertyValue "{key}" with value "{value}"')
@when('"{alice}" adds the PropertyValue "{key}" with value "{value}"')
@when('"{alice}" updates the PropertyValue "{key}" with value "{value}"')
async def add_property_value(context, alice, key, value):
    await publish_as(
        context,
        alice,
        "update_actor",
        {
            "actor": context.actors[alice].get("id"),
            "actions": [
                {
                    "action": "update_property_value",
                    "key": key,
                    "value": value,
                }
            ],
        },
    )


@when('"{alice}" removes the PropertyValue "{key}"')
async def remove_property_value(context, alice, key):
    await publish_as(
        context,
        alice,
        "update_actor",
        {
            "actor": context.actors[alice].get("id"),
            "actions": [
                {
                    "action": "remove_property_value",
                    "key": key,
                }
            ],
        },
    )


@then('The profile contains the property value "{key}" with value "{value}"')
def check_property_value(context, key, value):
    attachments = context.result.get("attachment", [])
    assert isinstance(attachments, list)

    result = list(filter(lambda x: x["name"] == key, attachments))[0]

    assert result["type"] == "PropertyValue"
    assert result["value"] == value


@then('The profile does not contain the property value "{key}"')
def check_not_property_value(context, key):
    attachments = context.result.get("attachment", [])
    assert isinstance(attachments, list)

    filtered = list(filter(lambda x: x["name"] == key, attachments))

    assert len(filtered) == 0
