"""Simple transformer type extension that adds the recipients and whether the activity is public to the data. You can
include this transformer into cattle_grid by adding

```toml title="cattle_grid.toml"
[[extensions]]
module = "cattle_grid.extensions.examples.recipients"
```

to your configuration file.

"""

from cattle_grid.extensions import Extension
from bovine.activitystreams.utils import recipients_for_object, is_public


extension = Extension("recipients", __name__)


@extension.transform(inputs=["raw"], outputs=["recipients"])
async def transformer(data):
    """The transformer

    ```pycon
    >>> from asyncio import run
    >>> run(transformer({"raw": {"type": "Activity", "to": ["http://alice.example"]}}))
    {'recipients': {'recipients': ['http://alice.example'], 'public': False}}

    ```
    """
    raw = data.get("raw")
    recipients = recipients_for_object(raw)
    public = is_public(raw)

    return {"recipients": {"recipients": list(recipients), "public": public}}
