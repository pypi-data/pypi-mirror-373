import json

from cattle_grid.model.lookup import Lookup

from .lookup import cache_lookup
from .testing import *  # noqa


async def test_cache_lookup_no_result(redis_client):
    lookup = Lookup(uri="http://actor.example/object", actor="http://actor.example")

    result = await cache_lookup(lookup, redis_client)

    assert isinstance(result, Lookup)

    assert lookup == result


async def test_cache_lookup_result(redis_client):
    uri = "http://actor.example/object"
    data = {"type": "FromCache"}
    lookup = Lookup(uri=uri, actor="http://actor.example")

    await redis_client.set(uri, json.dumps(data))

    result = await cache_lookup(lookup, redis_client)

    assert isinstance(result, Lookup)

    assert result.result == data
