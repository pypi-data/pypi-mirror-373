"""
This cache stores objects temporally in a key value database

Sample configuration

```toml title="cattle_grid.toml"
[[extensions]]
module = "cattle_grid.extensions.examples.cache"
lookup_order = 4
config = { connection_url = "redis://cattle_grid_redis", duration = 3600 }
```

The duration is expressed in seconds. By using the special
connection_url `:memory:` the cache will be replaced by
[fakeredis](https://fakeredis.readthedocs.io/en/latest/).
This means that the cache is in memory and no external key value
database is necessary. This is useful for testing, but not
recommended for production use.

"""

import logging
import json

from cattle_grid.model import ActivityMessage
from .dependencies import CacheClient

from contextlib import asynccontextmanager
from cattle_grid.extensions import Extension

from redis import asyncio as redis

from .lookup import cache_lookup
from .config import CacheConfiguration

logger = logging.getLogger(__name__)


extension = Extension(
    name="public data cache",
    module=__name__,
    config_class=CacheConfiguration,
)


@asynccontextmanager
async def lifespan(config: extension.Config):  # type: ignore
    import cattle_grid.extensions.examples.cache.dependencies as dependencies

    if config.connection_url == ":memory:":
        logger.info("Using in memory cache")

        import fakeredis

        async with fakeredis.FakeAsyncRedis() as client:
            dependencies.cache = client
            yield
    else:
        client = redis.from_url(config.connection_url)

        logger.info("Connected to redis %s", config.connection_url)

        dependencies.cache = client

        yield


extension.lifespan = lifespan


@extension.subscribe("incoming.Create")
async def handle_create_activity(
    activity: ActivityMessage,
    cache: CacheClient,
    config: extension.Config,  # type: ignore
) -> None:
    obj = activity.data.get("raw", {}).get("object")

    await cache.setex(obj.get("id"), config.duration, json.dumps(obj))


extension.lookup()(cache_lookup)
