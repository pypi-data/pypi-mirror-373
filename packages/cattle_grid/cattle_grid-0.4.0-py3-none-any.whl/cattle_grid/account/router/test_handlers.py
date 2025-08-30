import pytest
from unittest.mock import AsyncMock
from sqlalchemy import select
from cattle_grid.account.account import add_permission
from cattle_grid.database.account import Account, ActorForAccount

from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.model.account import CreateActorRequest
from .router import create_actor_handler


async def test_create_actor_handler_no_permission(sql_session_for_test):
    account = Account(name="test", password_hash="")
    sql_session_for_test.add(account)
    await sql_session_for_test.commit()
    broker = AsyncMock()

    with pytest.raises(ValueError):
        await create_actor_handler(
            CreateActorRequest(base_url="http://abel", preferred_username="username"),
            account=account,
            broker=broker,
            correlation_id="uuid",
            session=sql_session_for_test,
        )


async def test_create_actor_handler(sql_session_for_test):
    account = Account(name="test", password_hash="")
    sql_session_for_test.add(account)
    await sql_session_for_test.commit()
    await add_permission(sql_session_for_test, account, "admin")
    broker = AsyncMock()

    await create_actor_handler(
        CreateActorRequest(base_url="http://abel", preferred_username="username"),
        account=account,
        broker=broker,
        correlation_id="uuid",
        session=sql_session_for_test,
    )

    result = [x for x in await sql_session_for_test.scalars(select(ActorForAccount))]

    assert len(result) == 1

    broker.publish.assert_awaited_once()

    (data,) = broker.publish.call_args[0]

    assert data["id"] == result[0].actor
    assert data["preferredUsername"] == "username"
