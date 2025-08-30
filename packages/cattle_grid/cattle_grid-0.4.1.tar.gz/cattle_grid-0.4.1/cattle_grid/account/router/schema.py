from faststream import FastStream
from faststream.asyncapi.schema import Schema


from cattle_grid.version import __version__

from cattle_grid.model.account import EventInformation
from .router import create_router


def get_mock_faststream_app() -> FastStream:
    """Creates a mock faststream app for Account processing"""

    from faststream.rabbit import RabbitBroker

    broker = RabbitBroker()
    broker.include_router(create_router())

    broker.publisher(
        "incoming",
        title="receive.NAME.incoming",
        schema=EventInformation,
        description="""Incoming messages from the Fediverse""",
    )

    broker.publisher(
        "outgoing",
        title="receive.NAME.outgoing",
        schema=EventInformation,
        description="""Messages being sent towards the Fediverse""",
    )

    return FastStream(
        broker,
        title="cattle_grid Cattle Drive Implementation",
        version=__version__,
        description="Illustrates how cattle grid processes ActivityPub",
    )


def get_async_api_schema() -> Schema:
    """Returns the async api schema for cattle_grid Account processing"""
    from faststream.asyncapi import get_app_schema

    app = get_mock_faststream_app()

    return get_app_schema(app)
