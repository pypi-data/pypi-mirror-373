import uuid6
from urllib.parse import urlparse

from pydantic import BaseModel


def determine_url_start(actor_id, prefix):
    """
    Used to determine the url of a stored object

    ```pycon
    >>> determine_url_start("http://abel.example/actor/alice",
    ...     "/simple/storage/")
    'http://abel.example/simple/storage/'

    ```
    """
    parsed = urlparse(actor_id)

    return f"{parsed.scheme}://{parsed.netloc}{prefix}"


class SimpleStorageConfiguration(BaseModel):
    """Configuration of the simple storage extension"""

    prefix: str = "/simple_storage/"
    """
    Path to use before the generated uuid. The protocol and domain will be extracted from the actor id. See [cattle_grid.extensions.examples.simple_storage.config.determine_url_start][].
    """

    def url_start(self, actor_id):
        return determine_url_start(actor_id, self.prefix)

    def make_id(self, actor_id):
        new_uuid = uuid6.uuid7()
        return self.url_start(actor_id) + str(new_uuid), new_uuid
