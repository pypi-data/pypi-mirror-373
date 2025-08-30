from fast_depends import Depends
from typing import Annotated
from redis import asyncio as redis

from .config import CacheConfiguration

cache: redis.Redis | None = None

config: CacheConfiguration | None = None


def get_cache():
    global cache
    return cache


def get_config():
    global config
    return config


def set_config(cfg):
    global config
    config = cfg


CacheClient = Annotated[redis.Redis, Depends(get_cache)]
"""The cache client"""


CacheConfig = Annotated[CacheConfiguration, Depends(get_config)]
"""The configuration object passed when instantiating the extension"""
