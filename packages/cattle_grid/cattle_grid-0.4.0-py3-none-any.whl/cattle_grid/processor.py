from faststream import FastStream
from faststream.rabbit import RabbitBroker

import logging

from contextlib import asynccontextmanager

from .app import add_routers_to_broker, init_extensions

from .dependencies.globals import global_container

from .extensions.load import (
    lifespan_from_extensions,
)

logging.basicConfig(level=logging.DEBUG)

global_container.load_config()
extensions = init_extensions(global_container.config)

broker = RabbitBroker(global_container.config.amqp_uri)  # type:ignore

add_routers_to_broker(broker, extensions, global_container.config)


@asynccontextmanager
async def lifespan():
    async with global_container.common_lifecycle(global_container.config):
        async with lifespan_from_extensions(extensions):
            yield


app = FastStream(broker, lifespan=lifespan)


@app.after_startup
async def declare_exchanges() -> None:
    await broker.declare_exchange(global_container.internal_exchange)
    await broker.declare_exchange(global_container.exchange)
