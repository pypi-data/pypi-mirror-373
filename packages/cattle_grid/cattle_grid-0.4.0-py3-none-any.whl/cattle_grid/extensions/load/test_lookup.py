from cattle_grid.model.lookup import Lookup
from cattle_grid.extensions import Extension

from .lookup import ordered_lookups


async def lookup_1(lookup: Lookup) -> Lookup:
    return lookup


async def lookup_2(lookup: Lookup) -> Lookup:
    return lookup


async def lookup_3(lookup: Lookup) -> Lookup:
    return lookup


def test_ordered_lookups():
    one = Extension(name="one", lookup_method=lookup_1, lookup_order=0, module=__name__)
    two = Extension(name="two", lookup_method=lookup_2, lookup_order=2, module=__name__)
    three = Extension(
        name="three", lookup_method=lookup_3, lookup_order=1, module=__name__
    )

    result = ordered_lookups([one, two, three])

    assert result == [lookup_2, lookup_3, lookup_1]


def test_ordered_lookups_filters():
    one = Extension(name="one", module=__name__)

    result = ordered_lookups([one])

    assert len(result) == 0
