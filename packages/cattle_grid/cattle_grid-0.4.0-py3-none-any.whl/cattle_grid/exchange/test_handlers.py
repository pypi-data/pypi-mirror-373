from unittest.mock import AsyncMock

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.testing import mocked_config

from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.database.activity_pub_actor import PublicIdentifier

from cattle_grid.model.exchange import (
    UpdateActorMessage,
    UpdateIdentifierAction,
    UpdateActionType,
)
from .handlers import update_actor


async def test_update_actor(sql_session_for_test, actor_for_test):
    new_name = "Alyssa Newton"
    msg = UpdateActorMessage(actor=actor_for_test.actor_id, profile={"name": new_name})

    await update_actor(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )

    await sql_session_for_test.refresh(actor_for_test, attribute_names=["profile"])

    obj = actor_to_object(actor_for_test)

    assert obj.get("name") == new_name


async def test_update_actor_profile_not_overwritten(
    sql_session_for_test, actor_for_test
):
    new_name = "Alyssa Newton"
    new_description = "I was originally called Leibnitz. Also I'm a cat."
    msg = UpdateActorMessage(actor=actor_for_test.actor_id, profile={"name": new_name})

    await update_actor(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )
    await sql_session_for_test.refresh(actor_for_test)

    obj = actor_to_object(actor_for_test)
    assert obj.get("name") == new_name

    msg = UpdateActorMessage(
        actor=actor_for_test.actor_id, profile={"summary": new_description}
    )

    await update_actor(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )
    await sql_session_for_test.refresh(actor_for_test)

    obj = actor_to_object(actor_for_test)
    assert obj.get("name") == new_name


async def test_create_identifier(sql_session_for_test, actor_with_account):
    with mocked_config({"frontend": {"base_urls": ["http://localhost"]}}):
        identifier = "acct:new@localhost"
        new_identifier = UpdateIdentifierAction(
            action=UpdateActionType.create_identifier,
            identifier=identifier,
            primary=False,
        )

        msg = UpdateActorMessage(
            actor=actor_with_account.actor_id, actions=[new_identifier]
        )

        await update_actor(
            msg, actor_with_account, session=sql_session_for_test, broker=AsyncMock()
        )
        await sql_session_for_test.refresh(
            actor_with_account, attribute_names=["identifiers"]
        )

        obj = actor_to_object(actor_with_account)

        assert identifier in obj.get("identifiers", [])


async def test_update_identifier(sql_session_for_test, actor_for_test):
    identifier = "acct:one@localhost"
    sql_session_for_test.add_all(
        [
            PublicIdentifier(
                actor=actor_for_test,
                identifier="acct:two@localhost",
                name="through_exchange",
                preference=1,
            ),
            PublicIdentifier(
                actor=actor_for_test,
                identifier=identifier,
                name="through_exchange",
                preference=0,
            ),
        ]
    )
    await sql_session_for_test.commit()
    await sql_session_for_test.refresh(actor_for_test, attribute_names=["identifiers"])

    obj = actor_to_object(actor_for_test)

    assert obj["preferredUsername"] == "two"

    update_identifier = UpdateIdentifierAction(
        action=UpdateActionType.update_identifier,
        identifier=identifier,
        primary=True,
    )

    msg = UpdateActorMessage(actor=actor_for_test.actor_id, actions=[update_identifier])

    await update_actor(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )

    await sql_session_for_test.refresh(actor_for_test, attribute_names=["identifiers"])

    obj = actor_to_object(actor_for_test)

    assert obj["preferredUsername"] == "one"
