from faststream.rabbit import RabbitRouter, RabbitExchange, RabbitQueue
from typing import Any, List, Tuple

from cattle_grid.dependencies.globals import global_container

from .remote import fetch_object, sending_message
from .outgoing import create_outgoing_router
from .incoming import create_incoming_router
from .store_activity import store_activity_subscriber
from .shared_inbox import handle_shared_inbox_message


def create_processing_router(exchange: RabbitExchange | None = None) -> RabbitRouter:
    if exchange is None:
        exchange = global_container.internal_exchange

    router = RabbitRouter()
    router.include_router(create_outgoing_router(exchange))
    router.include_router(create_incoming_router(exchange))

    routing_config: List[Tuple[str, Any]] = [
        ("store_activity", store_activity_subscriber),
        ("to_send", sending_message),
        ("fetch_object", fetch_object),
        ("shared_inbox", handle_shared_inbox_message),
    ]
    for routing_key, coroutine in routing_config:
        router.subscriber(
            RabbitQueue(f"cg_internal_{routing_key}", routing_key=routing_key),
            exchange=exchange,
            title=f"Internal:{routing_key}",
        )(coroutine)

    return router
