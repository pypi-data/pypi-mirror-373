"""Implements loading the configuration"""

from dynaconf import Dynaconf

from typing import List

from .settings import get_settings


default_filenames = [
    "cattle_grid.toml",
    "cattle_grid_auth.toml",
    "cattle_grid_block_list.toml",
    "config/*.toml",
]


def load_settings(filenames: List[str] | None = None) -> Dynaconf:
    if filenames:
        return get_settings(filenames)
    else:
        return get_settings()
