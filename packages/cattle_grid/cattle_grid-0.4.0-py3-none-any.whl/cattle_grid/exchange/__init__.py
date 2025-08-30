import logging

from faststream import FastStream
from faststream.rabbit import RabbitRouter, RabbitExchange, RabbitQueue
from faststream.asyncapi.schema import Schema
from typing import Any, List, Tuple

from cattle_grid.version import __version__
from cattle_grid.dependencies.globals import global_container

from .info import add_method_information
from .handlers import update_actor, delete_actor_handler
from .message_handlers import send_message, fetch_object
from .shovel import incoming_shovel, outgoing_shovel

# from .data_types import ActivityMessage

logger = logging.getLogger(__name__)


def create_router(
    main_exchange: RabbitExchange | None = None, include_shovels=True
) -> RabbitRouter:
    """Creates a router to be used to manage users"""

    if main_exchange is None:
        main_exchange = global_container.exchange

    router = RabbitRouter()

    if include_shovels:
        router.subscriber(
            RabbitQueue("incoming_shovel", routing_key="incoming.#"),
            global_container.internal_exchange,
        )(incoming_shovel)
        router.subscriber(
            RabbitQueue("outgoing_shovel", routing_key="outgoing.#"),
            global_container.internal_exchange,
        )(outgoing_shovel)

    routing_config: List[Tuple[str, Any]] = [
        ("update_actor", update_actor),
        ("delete_actor", delete_actor_handler),
        ("send_message", send_message),
        ("fetch_object", fetch_object),
        ("add_method_information", add_method_information),
    ]

    prefix = "cattle_grid_"

    for routing_key, coroutine in routing_config:
        router.subscriber(
            RabbitQueue(prefix + routing_key, routing_key=routing_key),
            exchange=main_exchange,
            title=routing_key,
        )(coroutine)

    return router


def get_mock_faststream_app() -> FastStream:
    from faststream.rabbit import RabbitBroker

    broker = RabbitBroker()
    broker.include_router(create_router(include_shovels=False))

    # @broker.subscriber("incoming.#", exchange="cattle_grid")
    # async def incoming_subscriber(message: ActivityMessage) -> None:
    #     """
    #     This is a sample implementation of a subscriber
    #     for incoming messages. cattle_grid publishes on
    #     the routing key `incoming.ACTIVITY_TYPE` all messages that
    #     it is receiving from the Fediverse.
    #     """

    # @broker.subscriber("outgoing.#", exchange="cattle_grid")
    # async def outgoing_subscriber(message: ActivityMessage) -> None:
    #     """
    #     This is a sample implementation of a subscriber
    #     for outgoing messages. cattle_grid publishes on
    #     the routing key `outgoing.ACTIVITY_TYPE` all messages that
    #     it is sending to the Fediverse.

    #     This routing key is useful if you have multiple
    #     client implementations and expect them to stay in thing.

    #         To be determined:

    #         One needs messages to synchronize clients, e.g. I have
    #         read activity with URI id on this device. These might also be send through this exchange.
    #     """

    return FastStream(
        broker,
        title="cattle_grid exchange",
        version=__version__,
        description="Exchange in cattle_grid that applications using cattle_grid as middle ware are supposed to subscribe to",
    )


def get_async_api_schema() -> Schema:
    from faststream.asyncapi import get_app_schema

    app = get_mock_faststream_app()

    return get_app_schema(app)
