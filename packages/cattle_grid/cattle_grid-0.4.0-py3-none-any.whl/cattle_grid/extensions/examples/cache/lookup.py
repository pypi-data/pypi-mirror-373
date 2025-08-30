import json
import logging

from cattle_grid.model.lookup import Lookup

from .dependencies import CacheClient

logger = logging.getLogger(__name__)


async def cache_lookup(lookup: Lookup, cache: CacheClient) -> Lookup:
    cache_result = await cache.get(lookup.uri)

    logger.info("Got result from cache %s", cache_result)

    if not cache_result:
        return lookup

    lookup.result = json.loads(cache_result)

    logger.info(lookup)

    return lookup
