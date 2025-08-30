"""
The exchanges used by cattle_grid are using routing keys
to make processing easier. The cattle_grid gateway takes
these messages and readdresses them with routing keys
based on an user. Here an user can have multiple actors.

Furthermore, convenience methods are provided to manage
users and actors through a HTTP Api. This is in difference
to interacting with the Fediverse, which is done through a
message queue.
"""

from faststream.rabbit import RabbitRouter
from .router import create_router


def create_gateway_router() -> RabbitRouter:
    """Creates a router that moves messages to be routed by user."""
    gateway_router = RabbitRouter()
    gateway_router.include_router(create_router())

    return gateway_router
