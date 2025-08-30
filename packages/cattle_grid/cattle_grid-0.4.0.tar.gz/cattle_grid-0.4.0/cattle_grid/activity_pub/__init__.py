from faststream import FastStream
from faststream.asyncapi.schema import Schema
from fastapi import FastAPI

from cattle_grid.version import __version__

from .processing import create_processing_router
from .server import router


def get_mock_faststream_app() -> FastStream:
    """Creates a mock faststream app for ActivityPub processing"""

    from faststream.rabbit import RabbitBroker

    broker = RabbitBroker()
    broker.include_router(create_processing_router())

    return FastStream(
        broker,
        title="cattle_grid ActivityPub processing",
        version=__version__,
        description="Illustrates how cattle grid processes ActivityPub",
    )


def get_async_api_schema() -> Schema:
    """Returns the async api schema for cattle_grid ActivityPub processing"""
    from faststream.asyncapi import get_app_schema

    app = get_mock_faststream_app()

    return get_app_schema(app)


def get_fastapi_app() -> FastAPI:
    """Returns the fast api app for ActivityPub processing"""

    app = FastAPI(title="cattle_grid ActivityPub routes", version=__version__)
    app.include_router(router)

    return app
