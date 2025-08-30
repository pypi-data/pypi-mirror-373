import pytest

from sqlalchemy import select, func
from unittest.mock import AsyncMock, MagicMock
from cattle_grid.testing.fixtures import *  # noqa

from cattle_grid.database.activity_pub_actor import Follower, Following
from cattle_grid.model import ActivityMessage

from .incoming import (
    incoming_follow_request,
    incoming_accept_activity,
    incoming_reject_activity,
    incoming_delete_activity,
    incoming_block_activity,
    incoming_undo_activity,
)


@pytest.mark.parametrize(
    "object_creator", [lambda x: x, lambda x: {"type": "Person", "id": x}]
)
async def test_incoming_follow_request_create_follower(
    actor_for_test,
    object_creator,
    sql_session_for_test,
):
    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
            "object": object_creator(actor_for_test.actor_id),
        },
    )
    mock = AsyncMock()

    await incoming_follow_request(
        msg,
        factories=MagicMock(),
        actor=actor_for_test,
        broker=mock,
        session=sql_session_for_test,
    )

    followers = [x for x in await sql_session_for_test.scalars(select(Follower))]

    assert len(followers) == 1

    item = followers[0]
    assert item.follower == "http://remote.test/actor"
    assert not item.accepted

    mock.publish.assert_not_awaited()


async def test_incoming_follow_request_invalid(actor_for_test, sql_session_for_test):
    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
        },
    )
    await incoming_follow_request(
        msg,
        actor_for_test,
        factories=MagicMock(),
        broker=AsyncMock(),
        session=sql_session_for_test,
    )

    assert 0 == await sql_session_for_test.scalar(func.count(Follower.id))


async def test_incoming_follow_request_auto_follow(
    actor_for_test, sql_session_for_test
):
    actor_for_test.automatically_accept_followers = True
    await sql_session_for_test.merge(actor_for_test)

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Follow",
            "actor": "http://remote.test/actor",
            "object": actor_for_test.actor_id,
        },
    )
    mock = AsyncMock()

    factories = [MagicMock(), MagicMock()]
    factories[0].accept.return_value.build.return_value = {"id": "accept:1234"}

    await incoming_follow_request(
        msg,
        factories=factories,  # type: ignore
        actor=actor_for_test,
        broker=mock,
        session=sql_session_for_test,
    )

    mock.publish.assert_awaited_once()


async def test_incoming_accept_activity(sql_session_for_test, actor_for_test):
    follow_id = "follow:1234"
    remote = "http://remote.test/actor"

    following = Following(
        actor=actor_for_test, following=remote, request=follow_id, accepted=False
    )
    sql_session_for_test.add(following)
    await sql_session_for_test.commit()

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Accept",
            "actor": remote,
            "object": follow_id,
        },
    )
    await incoming_accept_activity(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )
    await sql_session_for_test.commit()

    await sql_session_for_test.refresh(following)

    assert following.accepted


async def test_incoming_accept_not_found(sql_session_for_test, actor_for_test):
    remote = "http://remote.test/actor"

    msg = ActivityMessage(
        actor=actor_for_test.actor_id,
        data={
            "id": "http://remote.test/id",
            "type": "Accept",
            "actor": remote,
            "object": "do_not_exist",
        },
    )
    await incoming_accept_activity(
        msg, actor_for_test, session=sql_session_for_test, broker=AsyncMock()
    )


async def test_incoming_reject(sql_session_for_test, actor_for_test):
    broker = AsyncMock()

    sql_session_for_test.add(
        Following(
            actor=actor_for_test,
            following="http://remote.test/",
            accepted=True,
            request="http://actor.test/follow",
        )
    )
    await sql_session_for_test.commit()

    await incoming_reject_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/reject",
                "type": "Reject",
                "actor": "http://remote.test",
                "object": "http://actor.test/follow",
            },
        ),
        actor_for_test,
        broker=broker,
        session=sql_session_for_test,
    )

    following_count = await sql_session_for_test.scalar(func.count(Following.id))

    assert following_count == 0


async def test_incoming_delete(sql_session_for_test, actor_for_test):
    sql_session_for_test.add_all(
        [
            Following(
                actor=actor_for_test,
                following="http://remote.test/",
                accepted=True,
                request="http://actor.test/follow",
            ),
            Follower(
                actor=actor_for_test,
                follower="http://remote.test/",
                accepted=True,
                request="http://actor.test/other",
            ),
        ]
    )

    await incoming_delete_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/delete",
                "type": "Delete",
                "actor": "http://remote.test/",
                "object": "http://remote.test/",
            },
        ),
        session=sql_session_for_test,
    )

    follower_count = await sql_session_for_test.scalar(func.count(Follower.id))
    following_count = await sql_session_for_test.scalar(func.count(Following.id))

    assert follower_count == 0
    assert following_count == 0


async def test_incoming_block(sql_session_for_test, actor_for_test):
    broker = AsyncMock()

    sql_session_for_test.add(
        Following(
            actor=actor_for_test,
            following="http://remote.test/",
            accepted=True,
            request="http://actor.test/follow",
        )
    )
    await sql_session_for_test.commit()

    await incoming_block_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/reject",
                "type": "Block",
                "actor": "http://remote.test/",
                "object": actor_for_test.actor_id,
            },
        ),
        broker=broker,
        actor=actor_for_test,
        session=sql_session_for_test,
    )

    following_count = await sql_session_for_test.scalar(func.count(Following.id))

    assert following_count == 0


@pytest.mark.parametrize(
    "object_builder",
    [
        lambda x: x,
        lambda x: {"type": "Follow", "id": x, "actor": "http://remote.test/"},
    ],
)
async def test_incoming_undo_follow(
    sql_session_for_test, actor_for_test, object_builder
):
    broker = AsyncMock()
    follow_request_id = "http://actor.test/follow"

    sql_session_for_test.add(
        Follower(
            actor=actor_for_test,
            follower="http://remote.test/",
            accepted=True,
            request=follow_request_id,
        )
    )
    await sql_session_for_test.commit()

    await incoming_undo_activity(
        ActivityMessage(
            actor=actor_for_test.actor_id,
            data={
                "id": "http://actor.test/follow/undo",
                "type": "Undo",
                "actor": "http://remote.test/",
                "object": object_builder(follow_request_id),
            },
        ),
        session=sql_session_for_test,
        broker=broker,
        actor=actor_for_test,
    )

    follower_count = await sql_session_for_test.scalar(func.count(Follower.id))

    assert follower_count == 0
