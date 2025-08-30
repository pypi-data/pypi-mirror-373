import pytest
from unittest.mock import AsyncMock

from faststream.rabbit import RabbitBroker, TestRabbitBroker, RabbitQueue

from bovine.activitystreams import factories_for_actor_object
from sqlalchemy import func, select

from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.database.activity_pub_actor import Follower, Blocking
from cattle_grid.model import ActivityMessage
from cattle_grid.dependencies.globals import global_container


from .outgoing import (
    create_outgoing_router,
    outgoing_message_distribution,
    outgoing_reject_activity,
    outgoing_block_activity,
    outgoing_undo_request,
)


@pytest.fixture
async def mock_subscriber():
    return AsyncMock()


@pytest.fixture
async def broker(mock_subscriber):
    br = RabbitBroker("amqp://guest:guest@localhost:5672/")
    br.include_router(create_outgoing_router())

    br.subscriber(
        RabbitQueue("test_queue", routing_key="to_send"),
        exchange=global_container.internal_exchange,
    )(mock_subscriber)

    async with TestRabbitBroker(br, connect_only=False) as tbr:
        yield tbr


async def test_outgoing_message_no_call(broker, mock_subscriber):
    try:
        await broker.publish(
            {},
            routing_key="outgoing.Activity",
            exchange=global_container.internal_exchange,
        )
    except Exception as e:
        print(e)

    mock_subscriber.assert_not_called()


async def test_outgoing_message(broker, mock_subscriber, actor_for_test):
    await broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": {"to": "http://remote"},
        },
        routing_key="outgoing.Activity",
        exchange=global_container.internal_exchange,
    )

    mock_subscriber.assert_awaited_once()


async def test_outgoing_message_follower(
    broker, sql_session_for_test, mock_subscriber, actor_for_test
):
    follower_id = "http://follower.test"
    sql_session_for_test.add(
        Follower(
            actor=actor_for_test, follower=follower_id, request="xxx", accepted=True
        )
    )
    await sql_session_for_test.commit()

    await broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": {"to": actor_for_test.followers_uri},
        },
        routing_key="outgoing.Activity",
        exchange=global_container.internal_exchange,
    )

    mock_subscriber.assert_awaited_once()
    args = mock_subscriber.call_args

    assert args[1].get("target") == follower_id


async def test_outgoing_follow_request(
    broker, sql_session_for_test, mock_subscriber, actor_for_test
):
    remote_actor = "http://remote"

    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    activity = activity_factory.follow(remote_actor, id="follow_id")

    await broker.publish(
        {"actor": actor_for_test.actor_id, "data": activity},
        routing_key="outgoing.Follow",
        exchange=global_container.internal_exchange,
    )

    await sql_session_for_test.refresh(actor_for_test, attribute_names=["following"])

    assert 1 == len(actor_for_test.following)

    assert not actor_for_test.following[0].accepted
    assert actor_for_test.following[0].following == remote_actor


async def test_outgoing_accept_request(
    broker, sql_session_for_test, mock_subscriber, actor_for_test
):
    follow_request_id = "http://remote/id"

    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    activity = activity_factory.accept(follow_request_id)

    sql_session_for_test.add(
        Follower(
            actor=actor_for_test,
            follower="http://remote",
            request=follow_request_id,
            accepted=False,
        )
    )
    await sql_session_for_test.commit()

    await broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": activity,
        },
        routing_key="outgoing.Accept",
        exchange=global_container.internal_exchange,
    )
    await sql_session_for_test.refresh(actor_for_test, attribute_names=["followers"])

    assert 1 == len(actor_for_test.followers)

    assert actor_for_test.followers[0].accepted


async def test_outgoing_no_message_for_public(sql_session_for_test, actor_for_test):
    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    broker = AsyncMock()

    activity = activity_factory.accept("http://remote").as_public().build()

    await outgoing_message_distribution(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data=activity,
        ),
        session=sql_session_for_test,
        broker=broker,
    )

    broker.publish.assert_not_awaited()


async def test_outgoing_reject(sql_session_for_test, actor_for_test):
    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    broker = AsyncMock()

    sql_session_for_test.add(
        Follower(
            actor=actor_for_test,
            follower="http://remote.test/",
            accepted=True,
            request="http://remote.test/follow",
        )
    )

    await sql_session_for_test.commit()

    activity = activity_factory.reject(
        "http://remote.test/follow", to={"http://remote.test/"}
    ).build()

    await outgoing_reject_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data=activity,
        ),
        actor=actor_for_test,
        session=sql_session_for_test,
        broker=broker,
    )

    follower_count = await sql_session_for_test.scalar(func.count(Follower.id))

    assert follower_count == 0


async def test_outgoing_block(sql_session_for_test, actor_for_test):
    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    broker = AsyncMock()

    sql_session_for_test.add(
        Follower(
            actor=actor_for_test,
            follower="http://remote.test/",
            accepted=True,
            request="http://remote.test/follow",
        )
    )
    await sql_session_for_test.commit()

    activity = activity_factory.block("http://remote.test/").build()

    await outgoing_block_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data=activity,
        ),
        session=sql_session_for_test,
        actor=actor_for_test,
        broker=broker,
    )
    await sql_session_for_test.commit()

    follower_count = await sql_session_for_test.scalar(func.count(Follower.id))

    assert follower_count == 0

    blocking_count = await sql_session_for_test.scalar(func.count(Blocking.id))
    assert blocking_count == 1


async def test_outgoing_block_then_undo(sql_session_for_test, actor_for_test):
    activity_factory, _ = factories_for_actor_object(actor_to_object(actor_for_test))

    broker = AsyncMock()
    block_id = "http://me.test/block_id"

    activity = activity_factory.block("http://remote.test/", id=block_id).build()

    await outgoing_block_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data=activity,
        ),
        session=sql_session_for_test,
        actor=actor_for_test,
        broker=broker,
    )
    await sql_session_for_test.commit()

    blocking_count = await sql_session_for_test.scalar(
        func.count(select(Blocking.id).where(Blocking.active).scalar_subquery())
    )
    assert blocking_count == 1

    undo = activity_factory.undo(activity).build()

    await outgoing_undo_request(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data=undo,
        ),
        actor=actor_for_test,
        session=sql_session_for_test,
        broker=broker,
    )
    blocking_count = await sql_session_for_test.scalar(
        func.count(select(Blocking.id).where(Blocking.active).scalar_subquery())
    )
    assert blocking_count == 0
