from unittest.mock import AsyncMock
import aiohttp

from cattle_grid.dependencies.globals import global_container
from cattle_grid.model.lookup import Lookup

from . import build_lookup, load_extension, collect_method_information


async def test_build_lookup():
    extensions = [
        load_extension({"module": "cattle_grid.extensions.examples.webfinger_lookup"})
    ]

    lookup = build_lookup(extensions)

    data = Lookup(uri="http://remote.example", actor="http://actor.example")

    global_container.session = AsyncMock(aiohttp.ClientSession)

    await lookup(data)

    global_container.session = None


async def test_collect_method_information():
    extensions = [
        load_extension({"module": "cattle_grid.extensions.examples.simple_storage"})
    ]

    method_information = collect_method_information(extensions)

    assert len(method_information) == 2

    assert {x.routing_key for x in method_information} == {
        "publish_activity",
        "publish_object",
    }
