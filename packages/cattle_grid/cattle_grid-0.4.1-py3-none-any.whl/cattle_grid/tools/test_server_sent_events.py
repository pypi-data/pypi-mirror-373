import pytest
import asyncio

from .server_sent_events import async_iterator_for_queue_and_task


@pytest.fixture
async def do_nothing_task():
    async def task_function(): ...

    return asyncio.create_task(task_function())


async def test_async_iterator_for_queue_and_task_stops_on_None():
    queue = asyncio.Queue()

    async def task_function():
        await queue.put(None)
        await asyncio.sleep(60)

    task = asyncio.create_task(task_function())

    iterator = async_iterator_for_queue_and_task(queue, task)

    async for _ in iterator:
        ...


async def test_async_iterator_for_queue_and_task_iterators(do_nothing_task):
    queue = asyncio.Queue()
    for x in ["one", "two", "three", None]:
        await queue.put(x)

    iterator = async_iterator_for_queue_and_task(queue, do_nothing_task)

    results = []

    async for x in iterator:
        results.append(x)

    assert results == ["one", "two", "three"]


async def test_heart_beat(do_nothing_task):
    queue = asyncio.Queue()

    iterator = async_iterator_for_queue_and_task(queue, do_nothing_task, timeout=0.01)

    result = await iterator.__anext__()

    assert result == ": <3"
