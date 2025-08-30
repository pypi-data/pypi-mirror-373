import pytest
from unittest.mock import AsyncMock

from faststream.rabbit import RabbitBroker, TestRabbitBroker, RabbitQueue

from cattle_grid.testing.fixtures import *  # noqa
from cattle_grid.dependencies.globals import global_container

from . import create_processing_router


@pytest.fixture
async def mock_subscriber():
    return AsyncMock()


@pytest.fixture
async def broker(mock_subscriber):
    br = RabbitBroker("amqp://guest:guest@localhost:5672/")
    br.include_router(create_processing_router())

    br.subscriber(
        RabbitQueue("test_queue", routing_key="incoming.Activity"),
        exchange=global_container.internal_exchange,
    )(mock_subscriber)

    async with TestRabbitBroker(br, connect_only=False) as tbr:
        yield tbr


async def test_shared_inbox(actor_for_test, broker, mock_subscriber):
    activity = {
        "actor": "http://remote.test/actor",
        "type": "Activity",
        "to": [actor_for_test.actor_id],
    }

    await broker.publish(
        {"data": activity},
        routing_key="shared_inbox",
        exchange=global_container.internal_exchange,
    )

    mock_subscriber.assert_awaited_once()
