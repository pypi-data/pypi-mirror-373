import pytest
from typing import AsyncIterator

import fakeredis
from redis import asyncio as redis


@pytest.fixture
async def redis_client() -> AsyncIterator[redis.Redis]:
    async with fakeredis.FakeAsyncRedis() as client:
        yield client
