import asyncio

from unittest.mock import AsyncMock, MagicMock
from contextlib import asynccontextmanager

from cattle_grid.model.account import EventType

from .streaming import get_message_streamer


async def test_get_message_streamer():
    broker = MagicMock()

    @asynccontextmanager
    async def connection():
        yield AsyncMock()

    broker._connection = connection()

    streamer = get_message_streamer(AsyncMock(), 0.1)

    result = streamer("account_name", EventType.incoming)

    assert isinstance(result[0], asyncio.Queue)
    assert isinstance(result[1], asyncio.Task)

    try:
        result[1].cancel()
    except Exception:
        ...
