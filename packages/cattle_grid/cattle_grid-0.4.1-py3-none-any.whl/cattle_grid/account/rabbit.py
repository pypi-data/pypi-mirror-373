"""
Implementation of a [HTTP auth backend for rabbitmq](https://github.com/rabbitmq/rabbitmq-server/tree/v3.13.x/deps/rabbitmq_auth_backend_http).

A possible configuration of RabbitMQ is

```conf title="/etc/rabbitmq/conf.d/03_http_auth.conf"
--8<-- "./resources/dev/03_http_auth.conf"
```

Here, we use `auth_backend = internal` for the user
corresponding to the `cattle_grid` processes. As cattle_grid
connects to RabbitMQ on startup, it cannot authenticate
itself.

"""

import logging

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse
from typing import Annotated

from cattle_grid.account.account import account_with_name_password
from cattle_grid.dependencies.fastapi import SqlSession


logger = logging.getLogger(__name__)

rabbit_router = APIRouter(prefix="/rabbitmq", tags=["rabbitmq"])


@rabbit_router.post("/user", response_class=PlainTextResponse)
async def user_auth(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: SqlSession,
) -> str:
    """Checks login with username/password"""
    user = await account_with_name_password(session, username, password)

    if not user:
        logger.warning("Failed login to message broker with username '%s'", username)
        return "deny"

    return "allow"


@rabbit_router.post("/vhost", response_class=PlainTextResponse)
async def vhost_auth(
    username: Annotated[str, Form()], vhost: Annotated[str, Form()]
) -> str:
    """Authentication for vhosts, currently only "/" is allowed"""
    if vhost != "/":
        logger.warning("User %s tried to access vhost %s", username, vhost)
        return "deny"
    return "allow"


@rabbit_router.post("/resource", response_class=PlainTextResponse)
async def resource_auth() -> str:
    """Always allowed"""
    return "allow"


def validate_routing_key(username: str, routing_key: str):
    """Rules for the routing key, e.g.

    ```pycon
    >>> validate_routing_key("alice", "send.alice.trigger")
    True

    >>> validate_routing_key("alice", "send.bob.trigger")
    False

    ```
    """
    if routing_key.startswith(f"send.{username}."):
        return True
    if routing_key.startswith(f"receive.{username}."):
        return True
    if routing_key == f"error.{username}":
        return True
    return False


@rabbit_router.post(
    "/topic",
    response_class=PlainTextResponse,
)
async def topic_auth(
    username: Annotated[str, Form()],
    name: Annotated[str, Form()],
    routing_key: Annotated[str, Form()],
) -> str:
    """Checks if topic is allowed. Currently allowed are

    ```
    exchange = "amq.topic"
    ```

    and the routing keys `send.username` and `receive.username`
    """
    if name != "amq.topic":
        logger.warning("User %s tried to access exchange %s", username, name)
        return "deny"
    if not validate_routing_key(username, routing_key):
        logger.warning(
            "User %s tried to subscribe to routing_key %s",
            username,
            routing_key,
        )
        return "deny"

    return "allow"


def app_for_schema():
    from fastapi import FastAPI

    app = FastAPI(title="Authentication API for RabbitMQ")
    app.include_router(rabbit_router)
    return app
