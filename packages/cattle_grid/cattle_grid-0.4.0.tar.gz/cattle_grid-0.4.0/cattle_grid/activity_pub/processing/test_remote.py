import json
import aiohttp
import pytest
import pydantic

from fast_depends import dependency_provider
from faststream.rabbit import RabbitBroker, TestRabbitBroker
from unittest.mock import AsyncMock, MagicMock
from collections import namedtuple

from cattle_grid.dependencies import get_client_session
from cattle_grid.dependencies.globals import global_container
from cattle_grid.testing.fixtures import *  # noqa


from .remote import fetch_object, sending_message, resolve_inbox


@pytest.fixture
async def session():
    session_mock = AsyncMock(aiohttp.ClientSession)

    async def get_mock():
        yield session_mock

    dependency_provider.dependency_overrides[get_client_session] = get_mock

    return session_mock


@pytest.fixture
async def broker():
    br = RabbitBroker("amqp://guest:guest@localhost:5672/")
    br.subscriber("to_send", global_container.internal_exchange)(sending_message)
    br.subscriber("fetch_object", global_container.internal_exchange)(fetch_object)

    async with TestRabbitBroker(br, connect_only=False) as tbr:
        yield tbr


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"actor": "http://alice"},
        {"uri": "http://object"},
    ],
)
async def test_fetch_invalid(broker, data, actor_for_test):
    from cattle_grid.dependencies.globals import global_container

    global_container.lookup = AsyncMock(
        return_value=MagicMock(result=None, uri="http://object")
    )

    with pytest.raises(pydantic.ValidationError):
        await broker.publish(
            data,
            routing_key="fetch_object",
            exchange=global_container.internal_exchange,
            rpc=True,
        )


async def test_fetch(broker, session, actor_for_test):
    expected = {"key": "value"}

    Result = namedtuple("http_result", ["status", "raise_for_status", "text"])

    result = Result(200, MagicMock(), AsyncMock(return_value=json.dumps(expected)))
    session.get = AsyncMock(return_value=result)

    from cattle_grid.dependencies.globals import global_container

    global_container.lookup = AsyncMock(
        return_value=MagicMock(result=None, uri="http://object")
    )

    response = await broker.publish(
        {"actor": actor_for_test.actor_id, "uri": "http://object"},
        routing_key="fetch_object",
        exchange=global_container.internal_exchange,
        rpc=True,
    )

    session.get.assert_awaited_once()

    assert response == expected


async def test_to_send_no_inbox(broker, session, actor_for_test):
    Result = namedtuple("http_result", ["status", "raise_for_status", "text"])

    result = Result(
        200,
        MagicMock(),
        AsyncMock(return_value=json.dumps({})),
    )
    session.get = AsyncMock(return_value=result)
    session.post = AsyncMock(return_value=result)

    await broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "target": "http://bob.test/actor",
            "data": {"type": "TestActivity"},
        },
        routing_key="to_send",
        exchange=global_container.internal_exchange,
    )

    session.get.assert_awaited_once()
    session.post.assert_not_called()


async def test_to_send(broker, session, actor_for_test):
    Result = namedtuple("http_result", ["status", "raise_for_status", "text"])

    result = Result(
        200,
        MagicMock(),
        AsyncMock(return_value=json.dumps({"inbox": "http://bob.test/inbox"})),
    )
    session.get = AsyncMock(return_value=result)
    session.post = AsyncMock(return_value=result)

    await broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "target": "http://bob.test/actor",
            "data": {"type": "TestActivity"},
        },
        routing_key="to_send",
        exchange=global_container.internal_exchange,
    )

    session.get.assert_awaited_once()
    session.post.assert_called_once()


async def test_resolve_inbox_no_inbox(sql_session_for_test):
    actor = AsyncMock()
    actor.get = AsyncMock(return_value={})

    result = await resolve_inbox(sql_session_for_test, actor, "target")
    assert result is None


async def test_resolve_inbox(sql_session_for_test):
    actor = AsyncMock()
    actor.get = AsyncMock(return_value={"inbox": "inbox"})

    result = await resolve_inbox(sql_session_for_test, actor, "target")
    assert result == "inbox"

    actor.get.assert_awaited_once()

    # inbox is cached
    result = await resolve_inbox(sql_session_for_test, actor, "target")
    actor.get.assert_awaited_once()
