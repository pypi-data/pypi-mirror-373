import asyncio
import logging
import aio_pika

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from uuid import uuid4

logger = logging.getLogger(__name__)


@asynccontextmanager
async def queue_for_connection(
    connection: aio_pika.RobustConnection,
    routing_key: str,
    name: str,
    exchange_name: str,
) -> AsyncGenerator[aio_pika.abc.AbstractQueue, None]:
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.get_exchange(exchange_name)

        queue = await channel.declare_queue(
            f"queue-{name}-{uuid4()}",
            durable=False,
            auto_delete=True,
            exclusive=True,
        )
        await queue.bind(exchange, routing_key=routing_key)

        yield queue


async def enqueue_to_routing_key_and_connection(
    connection: aio_pika.RobustConnection,
    asyncio_queue: asyncio.Queue,
    routing_key: str,
    name: str = "cattle-grid",
    exchange_name: str = "amq.topic",
):
    """Subscribes to the routing key and adds all
    the received messages to `asyncio_queue` as a string"""

    async with queue_for_connection(
        connection, routing_key=routing_key, name=name, exchange_name=exchange_name
    ) as queue:
        async with queue.iterator() as iterator:
            try:
                async for message in iterator:
                    async with message.process():
                        message_body = message.body.decode()
                        await asyncio_queue.put(message_body)
            except Exception as e:
                logger.exception(e)
