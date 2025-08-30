from contextlib import asynccontextmanager
from typing import Callable, List, AsyncContextManager, Any
from fast_depends import inject
from fastapi import FastAPI

from cattle_grid.dependencies.globals import global_container
from cattle_grid.extensions import Extension
from cattle_grid.model.extension import AddMethodInformationMessage


def collect_lifespans(
    extensions: List[Extension],
) -> List[Callable[[Any], AsyncContextManager]]:
    """Collects the lifespans from the extensions"""
    return [extension.lifespan for extension in extensions if extension.lifespan]


@asynccontextmanager
async def iterate_lifespans(lifespans: List[Callable[[Any], AsyncContextManager]]):
    if len(lifespans) == 0:
        yield
        return

    async with inject(lifespans[0])():  # type: ignore
        if len(lifespans) == 1:
            yield
        else:
            async with iterate_lifespans(lifespans[1:]):
                yield


def lifespan_for_extension(extension: Extension, include_broker: bool = False):
    broker = None

    if include_broker and extension.activity_router:
        broker = global_container.broker
        broker.include_router(extension.activity_router)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with global_container.common_lifecycle():
            if broker:
                await broker.start()

                await broker.publish(
                    AddMethodInformationMessage(
                        method_information=extension.method_information
                    ),
                    exchange=global_container.exchange,
                    routing_key="add_method_information",
                )

            if extension.lifespan:
                async with inject(extension.lifespan)():  # type: ignore
                    yield
            else:
                yield

            if broker:
                await broker.close()

    return lifespan
