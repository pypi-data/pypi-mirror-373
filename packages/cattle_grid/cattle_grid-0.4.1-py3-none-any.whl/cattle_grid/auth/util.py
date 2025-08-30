from urllib.request import urlopen
from urllib.parse import urlparse
from typing import Set
import logging

from bovine import BovineActor
from cattle_grid.config.auth import AuthConfig

logger = logging.getLogger(__name__)


def blocklist_form_url_or_file(url_or_file: str) -> Set[str]:
    if url_or_file.startswith("https://"):
        with urlopen(url_or_file) as f:
            data = [x.decode("utf-8") for x in f.readlines()]
    else:
        with open(url_or_file) as f:
            data = f.readlines()

    result = {
        x.removesuffix("\n") for x in data if x != "canary.fedinuke.example.com\n"
    }

    return result


def config_to_bovine_actor(auth_config: AuthConfig) -> BovineActor:
    return BovineActor(
        actor_id=auth_config.actor_id,
        secret=auth_config.private_key,
        public_key_url=auth_config.actor_id + "#mykey",
    )


def check_block(domain_blocks: Set[str], controller: str) -> bool:
    """Checks if a controller's domain is in block list

    ```pycon
    >>> check_block({"blocked.example"}, "http://actor.example/path")
    False

    >>> check_block({"blocked.example"}, "http://blocked.example/path")
    True

    ```
    """
    try:
        domain = urlparse(controller).netloc
        return domain in domain_blocks
    except Exception as e:
        logger.warning("Something went wrong with %s", repr(e))
        return True
