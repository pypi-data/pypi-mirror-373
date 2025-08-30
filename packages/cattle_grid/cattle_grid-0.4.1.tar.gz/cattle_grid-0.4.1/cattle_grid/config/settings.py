from dynaconf import Dynaconf

from typing import List

from .validators import all_validators


def get_settings(
    filenames: List[str] = [
        "cattle_grid.toml",
        "cattle_grid_auth.toml",
        "cattle_grid_block_list.toml",
        "config/*.toml",
    ],
) -> Dynaconf:
    return Dynaconf(
        settings_files=filenames,
        envvar_prefix="CATTLE_GRID",
        validators=all_validators,
    )
