import importlib
import logging

from contextlib import asynccontextmanager
from typing import List, Callable, Awaitable, Dict
from fast_depends import inject
from fastapi import FastAPI
from faststream.rabbit import RabbitBroker

from cattle_grid.model.extension import MethodInformationModel
from cattle_grid.extensions import Extension
from cattle_grid.model.lookup import LookupMethod, Lookup

from .util import get_transformers, transformation_steps
from .lookup import ordered_lookups
from .lifespan import iterate_lifespans, collect_lifespans

logger = logging.getLogger(__name__)


def load_extension(extension_information: dict) -> Extension:
    """Loads a single extension"""
    module_name = extension_information.get("module")

    if module_name is None:
        raise ValueError("module is required")

    module = importlib.import_module(module_name)
    extension = module.extension
    extension.configure(extension_information.get("config", {}))

    if extension.description is None and module.__doc__ is not None:
        extension.description = module.__doc__

    if "lookup_order" in extension_information:
        extension.lookup_order = extension_information["lookup_order"]
    if "api_prefix" in extension_information:
        extension.api_prefix = extension_information["api_prefix"]

    return extension


def load_extensions(settings) -> List[Extension]:
    """Loads the extensions from settings"""

    extensions = [
        load_extension(extension_information)
        for extension_information in settings.extensions
    ]

    logger.info("Loaded extensions: %s", ", ".join(f"'{e.name}'" for e in extensions))

    return extensions


def build_transformer(extensions: List[Extension]) -> Callable[[Dict], Awaitable[Dict]]:
    """Build the transformer"""
    transformers = get_transformers(extensions)
    steps = transformation_steps(transformers)

    async def transformer(data: dict):
        for step in steps:
            for plugin in step:
                data.update(await plugin.transformer(data))

        return data

    return transformer


def build_lookup(extensions: List[Extension]) -> LookupMethod:
    """Builds the lookup method"""
    methods = ordered_lookups(extensions)

    async def lookup_result(lookup: Lookup) -> Lookup:
        for method in methods:
            lookup = await inject(method)(lookup)
            if lookup.result is not None:
                return lookup
        return lookup

    return lookup_result


def set_globals(extensions: List[Extension]):
    """Sets global variables in cattle_grid.dependencies"""
    from cattle_grid.dependencies.globals import global_container

    global_container.transformer = build_transformer(extensions)
    global_container.lookup = build_lookup(extensions)


@asynccontextmanager
async def lifespan_from_extensions(extensions: List[Extension]):
    """Creates the lifespan from the extensions"""
    lifespans = collect_lifespans(extensions)

    async with iterate_lifespans(lifespans):
        yield


def add_routers_to_broker(broker: RabbitBroker, extensions: List[Extension]):
    """Adds the routers to the broker"""

    for extension in extensions:
        if extension.activity_router:
            broker.include_router(extension.activity_router)


def add_routes_to_api(app: FastAPI, extensions: List[Extension]):
    """Adds the routes to the api"""
    for extension in extensions:
        if extension.api_router:
            if extension.api_prefix:
                app.include_router(extension.api_router, prefix=extension.api_prefix)


def collect_method_information(
    extensions: List[Extension],
) -> List[MethodInformationModel]:
    """Collects the method information from the extensions"""
    return sum((extension.method_information for extension in extensions), [])
