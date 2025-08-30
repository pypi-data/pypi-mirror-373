from faststream.rabbit import RabbitBroker

from typing import List

from cattle_grid.extensions import Extension

from cattle_grid.account.router import create_gateway_router
from cattle_grid.activity_pub.processing import create_processing_router
from cattle_grid.exchange import create_router
from cattle_grid.testing.reporter import create_reporting_router
from cattle_grid.extensions.load import (
    add_routers_to_broker as extensions_add_routers_to_broker,
    load_extensions,
    set_globals,
    collect_method_information,
)
from cattle_grid.exchange.info import exchange_method_information
from cattle_grid.dependencies.globals import global_container


def add_routers_to_broker(broker: RabbitBroker, extensions: List[Extension], settings):
    broker.include_router(create_gateway_router())
    broker.include_router(create_processing_router(global_container.internal_exchange))

    if settings.enable_reporting:
        broker.include_router(create_reporting_router())

    broker.include_router(create_router())

    extensions_add_routers_to_broker(broker, extensions)


def init_extensions(settings):
    extensions = load_extensions(settings)

    set_globals(extensions)

    global_container.method_information = (
        collect_method_information(extensions) + exchange_method_information
    )

    return extensions
