import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.future import select

from cattle_grid.testing.fixtures import *  # noqa

from . import lifespan, simple_storage_publish_activity, simple_storage_publish_object
from .config import SimpleStorageConfiguration
from .message_types import PublishActivity, PublishObject
from .models import StoredActivity, StoredObject

activity_stub = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "AnimalSound",
    "actor": "http://alice.example",
    "to": ["http://bob.example"],
    "content": "moo",
}

object_stub = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Note",
    "attributedTo": "http://alice.example",
    "to": ["http://bob.example"],
    "content": "moo",
}


@pytest.fixture(autouse=True)
async def sql_engine(sql_engine_for_tests):
    async with lifespan(sql_engine_for_tests):
        yield sql_engine_for_tests


@pytest.mark.parametrize(
    "actor,activity",
    [
        ("http://bob.example", activity_stub),
        (
            "http://alice.example",
            {**activity_stub, "id": "http://alice.example/activity1"},
        ),
    ],
)
async def test_simple_storage_publish_activity_errors(actor, activity):
    msg = PublishActivity(
        actor=actor,
        data=activity,
    )

    with pytest.raises(ValueError):
        await simple_storage_publish_activity(
            msg, AsyncMock(), MagicMock(), AsyncMock()
        )


async def test_simple_storage_activity(sql_engine):
    msg = PublishActivity(actor="http://alice.example", data=activity_stub)

    broker = AsyncMock()
    config = SimpleStorageConfiguration(prefix="/simple/storage/")

    async_session = async_sessionmaker(sql_engine, expire_on_commit=False)

    async with async_session() as session:
        await simple_storage_publish_activity(
            msg, config, broker=broker, session=session
        )
        await session.commit()

    broker.publish.assert_awaited_once()

    async with async_session() as session:
        result = (await session.scalars(select(StoredActivity))).all()

        assert len(result) == 1

        assert result[0].data.get("id")


@pytest.mark.parametrize(
    "actor,object",
    [
        ("http://bob.example", object_stub),
        (
            "http://alice.example",
            {**object_stub, "id": "http://alice.example/activity1"},
        ),
    ],
)
async def test_simple_storage_publish_object_errors(actor, object):
    msg = PublishObject(
        actor=actor,
        data=object,
    )

    with pytest.raises(ValueError):
        await simple_storage_publish_object(msg, AsyncMock(), MagicMock(), AsyncMock())


async def test_simple_storage_object(sql_engine, actor_for_test):
    obj = object_stub.copy()
    obj["attributedTo"] = actor_for_test.actor_id
    msg = PublishObject(actor=actor_for_test.actor_id, data=obj)

    broker = AsyncMock()
    config = SimpleStorageConfiguration(prefix="/simple/storage/")

    async_session = async_sessionmaker(sql_engine, expire_on_commit=False)

    async with async_session() as session:
        await simple_storage_publish_object(
            msg, config, actor=actor_for_test, broker=broker, session=session
        )
        await session.commit()

    broker.publish.assert_awaited_once()

    async with async_session() as session:
        result = (await session.scalars(select(StoredActivity))).all()

        assert len(result) == 1

        assert result[0].data.get("id")

        result = (await session.scalars(select(StoredObject))).all()

        assert len(result) == 1

        assert result[0].data.get("id")
