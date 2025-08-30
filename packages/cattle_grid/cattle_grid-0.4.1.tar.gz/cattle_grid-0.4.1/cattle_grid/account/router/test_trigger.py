from unittest.mock import AsyncMock

from sqlalchemy import select

from cattle_grid.testing import mocked_config
from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.model.account import TriggerMessage

from cattle_grid.account.account import add_actor_to_group
from cattle_grid.database.account import ActorForAccount


from .trigger import handle_trigger


async def test_handle_trigger(sql_session_for_test, actor_with_account):
    broker = AsyncMock()
    actor_for_account = await sql_session_for_test.scalar(
        select(ActorForAccount).where(
            ActorForAccount.actor == actor_with_account.actor_id
        )
    )
    assert actor_for_account

    await handle_trigger(
        TriggerMessage(
            actor=actor_with_account.actor_id,  # type:ignore
        ),
        session=sql_session_for_test,
        actor=actor_for_account,
        broker=broker,
        correlation_id="uuid",
        method="method",
    )

    broker.publish.assert_awaited_once()

    (_, kwargs) = broker.publish.call_args

    assert kwargs["routing_key"] == "method"
    assert kwargs["correlation_id"] == "uuid"


async def test_handle_trigger_with_rewrite(sql_session_for_test, actor_with_account):
    broker = AsyncMock()
    actor_for_account = await sql_session_for_test.scalar(
        select(ActorForAccount).where(
            ActorForAccount.actor == actor_with_account.actor_id
        )
    )
    assert actor_for_account

    await add_actor_to_group(sql_session_for_test, actor_for_account, "group")

    config = {
        "rewrite": {
            "group": {
                "method": "changed",
            }
        }
    }

    with mocked_config(config):
        await handle_trigger(
            TriggerMessage(
                actor=actor_with_account.actor_id,
            ),
            session=sql_session_for_test,
            actor=actor_for_account,
            broker=broker,
            correlation_id="uuid",
            method="method",
        )

    broker.publish.assert_awaited_once()

    (_, kwargs) = broker.publish.call_args

    assert kwargs["routing_key"] == "changed"
    assert kwargs["correlation_id"] == "uuid"
