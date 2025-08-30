from unittest.mock import AsyncMock, MagicMock
import asyncio
import pytest
from .enqueuer import enqueue_from_inbox


@pytest.fixture
async def mock_broker():
    return AsyncMock()


async def test_enqueue_from_inbox_requires_type(mock_broker):
    await enqueue_from_inbox(mock_broker, MagicMock(), "actor_id", {})

    await asyncio.sleep(0.1)

    mock_broker.publish.assert_not_awaited()


async def test_enqueue_from_inbox(mock_broker):
    await enqueue_from_inbox(
        mock_broker, MagicMock(), "actor_id", {"type": "Test", "actor": "my_actor"}
    )

    await asyncio.sleep(0.1)

    mock_broker.publish.assert_awaited_once()
