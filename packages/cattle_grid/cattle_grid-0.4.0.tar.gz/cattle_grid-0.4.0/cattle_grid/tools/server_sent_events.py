import asyncio
import logging

from fastapi import Request
from fastapi.responses import StreamingResponse

from bovine.types import ServerSentEvent

logger = logging.getLogger(__name__)


async def async_iterator_for_queue_and_task(
    queue: asyncio.Queue, task, timeout: float = 0.2
):
    try:
        while True:
            try:
                async with asyncio.timeout(timeout):
                    result = await queue.get()
                    if result is None:
                        raise asyncio.CancelledError()
            except TimeoutError:
                logger.debug("Sending heartbeat")
                result = ": <3"
            yield result
    except asyncio.CancelledError:
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass
    except Exception as e:
        logger.exception(e)


def ServerSentEventFromAsyncIterator(
    request: Request, async_iterator
) -> StreamingResponse:
    async def event_stream():
        async for message in async_iterator:
            if await request.is_disconnected():
                return
            data = ServerSentEvent(data=message).encode()
            yield data

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def ServerSentEventFromQueueAndTask(
    request: Request, queue: asyncio.Queue, task: asyncio.Task, timeout: float = 50
):
    """The task is supposed to add strings to queue via
    `await queue.put(some_string)`.

    ```python
    from fastapi import Request

    @fastapi.get("/stream")
    def sample_stream(request: Request):
        queue = asyncio.Queue()
        task = asyncio.create_task(method_to_add_elements_to_queue(queue))

        return ServerSentEventFromQueueAndTask(request, queue, task)
    ```
    """

    async_iterator = async_iterator_for_queue_and_task(queue, task, timeout=timeout)
    return ServerSentEventFromAsyncIterator(request, async_iterator)
