from fastapi import FastAPI

from faststream import FastStream
from faststream.rabbit import RabbitBroker
from faststream.asyncapi import get_app_schema
from faststream.asyncapi.schema import Schema

from . import Extension
from .load.lifespan import lifespan_for_extension


def async_schema_for_extension(extension: Extension) -> Schema:
    """Converts the activity router of the extension to
    a [Schema][faststream.asyncapi.schema.Schema].

    this can be converted to a json string via
    `result.to_json()`."""
    broker = RabbitBroker()
    broker.include_router(extension.activity_router)

    app = FastStream(broker, title=extension.name)

    return get_app_schema(app)


def fastapi_for_extension(
    extension: Extension, include_broker: bool = False
) -> FastAPI:
    """Converts the api router of the extension to a
    [FastAPI][fastapi.FastAPI] app."""

    app = FastAPI(
        title=extension.name,
        description=extension.description or "",
        lifespan=lifespan_for_extension(extension, include_broker=include_broker),
    )

    app.include_router(extension.api_router)
    return app


def openapi_schema_for_extension(extension: Extension) -> dict:
    """Converts the api router of the extension to a
    dictionary containing the openapi schema"""
    app = fastapi_for_extension(extension)

    return app.openapi()
