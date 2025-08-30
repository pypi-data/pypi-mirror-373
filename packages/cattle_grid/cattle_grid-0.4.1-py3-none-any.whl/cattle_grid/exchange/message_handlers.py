import logging

from faststream import Context
from faststream.rabbit import RabbitBroker


from cattle_grid.activity_pub.enqueuer import determine_activity_type
from cattle_grid.model import ActivityMessage, FetchMessage
from cattle_grid.dependencies.globals import global_container

logger = logging.getLogger(__name__)


async def send_message(
    msg: ActivityMessage,
    broker: RabbitBroker = Context(),
) -> None:
    """Takes a message and ensure it is distributed appropriately

    FIXME: out_transformer?"""

    content = msg.data
    activity_type = determine_activity_type(content)

    if not activity_type:
        return

    to_send = ActivityMessage(actor=msg.actor, data=content)

    await broker.publish(
        to_send,
        exchange=global_container.exchange,
        routing_key=f"outgoing.{activity_type}",
    )
    await broker.publish(
        to_send,
        exchange=global_container.internal_exchange,
        routing_key=f"outgoing.{activity_type}",
    )


async def fetch_object(msg: FetchMessage, broker: RabbitBroker = Context()) -> dict:
    """Used to fetch an object as an RPC method"""
    result = await broker.publish(
        msg,
        routing_key="fetch_object",
        exchange=global_container.internal_exchange,
        rpc=True,
    )
    if result == b"" or result is None:
        return {}
    return result
