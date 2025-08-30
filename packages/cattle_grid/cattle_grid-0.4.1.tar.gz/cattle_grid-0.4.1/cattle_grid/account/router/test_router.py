import pytest

from unittest.mock import AsyncMock

from faststream.rabbit import RabbitBroker, TestRabbitBroker, RabbitQueue

from cattle_grid.activity_pub.actor import create_actor
from cattle_grid.testing.fixtures import *  # noqa

from .router import create_router
from cattle_grid.database.account import Account, ActorForAccount
from cattle_grid.model.extension import MethodInformationModel
from cattle_grid.dependencies.globals import global_container


@pytest.fixture
async def subscriber_mock():
    return AsyncMock()


@pytest.fixture
async def receive_subscriber_mock():
    return AsyncMock()


@pytest.fixture
async def test_account(sql_session_for_test):
    account = Account(name="alice", password_hash="password")
    sql_session_for_test.add(account)
    await sql_session_for_test.commit()
    return account


@pytest.fixture
async def test_actor(sql_session_for_test, test_account):
    actor = await create_actor(
        sql_session_for_test, "http://localhost/", preferred_username="alice"
    )
    sql_session_for_test.add(
        ActorForAccount(actor=actor.actor_id, account=test_account)
    )
    await sql_session_for_test.commit()
    return actor


@pytest.fixture
async def test_broker(subscriber_mock, receive_subscriber_mock):
    br = RabbitBroker("amqp://guest:guest@localhost:5672/")
    br.include_router(create_router())

    async def mock(msg):
        await subscriber_mock(msg)

        return {"type": "Person", "data": "blank"}

    br.subscriber("send_message", exchange=global_container.exchange)(mock)
    br.subscriber("fetch_object", exchange=global_container.internal_exchange)(mock)

    @br.subscriber(
        RabbitQueue("queue2", routing_key="receive.*.response.*"),
        exchange=global_container.account_exchange,
    )
    async def receive_mock(msg):
        await receive_subscriber_mock(msg)

    async with TestRabbitBroker(br) as tbr:
        yield tbr


async def test_fetch_nothing_happens(test_broker, subscriber_mock):
    await test_broker.publish(
        {"uri": "http://remote/ap/actor/bob"},
        routing_key="send.alice.request.fetch",
        exchange=global_container.account_exchange,
    )

    subscriber_mock.assert_not_called()


async def test_fetch_requires_actor(sql_session_for_test, test_broker, subscriber_mock):
    account = Account(name="alice", password_hash="password")
    actor = await create_actor(
        sql_session_for_test, "http://localhost/", preferred_username="alice"
    )
    sql_session_for_test.add_all(
        [account, ActorForAccount(actor=actor.actor_id, account=account)]
    )
    await sql_session_for_test.commit()

    fetch_uri = "http://remote/ap/actor/bob"

    await test_broker.publish(
        {
            "uri": fetch_uri,
            "actor": "http://localhost/other",
        },
        routing_key="send.alice.request.fetch",
        exchange=global_container.account_exchange,
    )

    subscriber_mock.assert_not_called()


async def test_fetch(test_broker, subscriber_mock, test_actor):
    fetch_uri = "http://remote/ap/actor/bob"

    await test_broker.publish(
        {"uri": fetch_uri, "actor": test_actor.actor_id},
        routing_key="send.alice.request.fetch",
        exchange=global_container.account_exchange,
    )

    subscriber_mock.assert_called_once()
    args = subscriber_mock.call_args[0][0]

    assert args["uri"] == fetch_uri
    assert args["actor"] == test_actor.actor_id


async def test_getting_info(test_broker, receive_subscriber_mock, test_actor):
    global_container.method_information = [
        MethodInformationModel(routing_key="test", module="test")
    ]

    await test_broker.publish(
        {"action": "info", "data": {}, "actor": ""},
        routing_key="send.alice.request.info",
        exchange=global_container.account_exchange,
    )

    receive_subscriber_mock.assert_called_once()
    args = receive_subscriber_mock.call_args[0][0]

    assert args["actors"] == [{"id": test_actor.actor_id, "name": "NO NAME"}]

    assert len(args["methodInformation"]) > 0
