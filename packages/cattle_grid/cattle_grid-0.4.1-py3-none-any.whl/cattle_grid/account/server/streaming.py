import asyncio
import logging
import aio_pika

from cattle_grid.dependencies.fastapi import Broker
from cattle_grid.model.account import EventType

from cattle_grid.tools import enqueue_to_routing_key_and_connection

logger = logging.getLogger(__name__)


async def enqueue_events(
    asyncio_queue, connection, account_name: str, event_type: EventType
):
    routing_key = f"receive.{account_name}.{event_type.value}"

    await enqueue_to_routing_key_and_connection(
        connection, asyncio_queue, routing_key=routing_key, name=account_name
    )


def get_message_streamer(broker: Broker, timeout: float = 5):
    if broker._connection is None:
        raise RuntimeError("Broker not connected")

    connection: aio_pika.RobustConnection = broker._connection

    def stream_messages(account_name: str, event_type: EventType):
        queue = asyncio.Queue()
        task = asyncio.create_task(
            enqueue_events(queue, connection, account_name, event_type)
        )
        return queue, task

    return stream_messages
