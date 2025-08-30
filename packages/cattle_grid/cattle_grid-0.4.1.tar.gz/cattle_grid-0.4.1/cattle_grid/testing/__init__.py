import logging


from contextlib import contextmanager
from dynaconf import Dynaconf
from dynaconf.utils import DynaconfDict

from cattle_grid.dependencies.globals import global_container

logger = logging.getLogger(__name__)


@contextmanager
def mocked_config(config: Dynaconf | dict):
    """overrides the configuration stored in `global_container.config`
    with the value in dict, afterwards resets the original value."""
    if isinstance(config, dict):
        config = DynaconfDict(config)
    old_config = global_container.config

    global_container._config = config

    yield

    global_container._config = old_config
