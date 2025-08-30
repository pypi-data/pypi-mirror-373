"""
Puts performing a webfinger lookup in the processing chain.
In a production setting, one can include this extension
via

```toml title="cattle_grid.toml"
[[extensions]]
module = "cattle_grid.extensions.examples.webfinger_lookup"

lookup_order = 10
```

Where the higher the `lookup_order`, the earlier the conversion from `acct` to resolvable URI happens.

In a test setting, one can make webfinger use http via

```toml title="cattle_grid.toml"
[[extensions]]
module = "cattle_grid.extensions.examples.webfinger_lookup"

config = { protocol = "http" }
```

"""

from pydantic import BaseModel, Field
from enum import StrEnum, auto

from bovine.clients import lookup_uri_with_webfinger

from cattle_grid.model.lookup import Lookup
from cattle_grid.extensions import Extension
from cattle_grid.dependencies import ClientSession


class Protocol(StrEnum):
    """Protocol to use for webfinger lookups"""

    http = auto()
    https = auto()


class WebfingerLookupConfig(BaseModel):
    """Configuration for the webfinger lookup"""

    protocol: Protocol = Field(
        default=Protocol.https, description="""protocol to use, defaults to https"""
    )


def build_domain(config: WebfingerLookupConfig, acct_uri: str) -> str:
    """Builds the domain to use for webfinger lookups

    ```pycon
    >>> build_domain(WebfingerLookupConfig(protocol=Protocol.http),
    ...     "acct:alice@server.example")
    'http://server.example'

    ```
    """
    return f"{config.protocol}://{acct_uri.split('@')[1]}"


extension = Extension("webfinger", module=__name__, config_class=WebfingerLookupConfig)


@extension.lookup()
async def lookup(
    lookup: Lookup,
    session: ClientSession,
    config: extension.Config,  # type:ignore
) -> Lookup:
    if lookup.uri.startswith("acct:"):
        uri, _ = await lookup_uri_with_webfinger(
            session, lookup.uri, domain=build_domain(config, lookup.uri)
        )

        if uri:
            lookup.uri = uri
    return lookup
