from . import load_extension

from .util import resolvable_transformers, get_transformers
from .types import Transformer


async def transformer(d: dict) -> dict:
    return d


one = Transformer(
    name="one",
    transformer=transformer,
    inputs={"raw"},
    outputs={"one"},
)

two = Transformer(
    name="two",
    transformer=transformer,
    inputs={"one"},
    outputs={"two"},
)


def test_resolvable_transformer_one():
    assert resolvable_transformers({one}, {"raw"}) == {one}


def test_get_transformers():
    extensions = load_extension(
        {"module": "cattle_grid.extensions.examples.recipients"}
    )

    transformers = get_transformers([extensions])

    assert len(transformers) == 1
    assert isinstance(list(transformers)[0], Transformer)
