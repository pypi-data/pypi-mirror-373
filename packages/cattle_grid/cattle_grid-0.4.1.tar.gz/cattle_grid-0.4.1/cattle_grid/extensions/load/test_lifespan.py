from unittest.mock import MagicMock
from contextlib import asynccontextmanager

from .lifespan import iterate_lifespans


def call_from_context(func):
    @asynccontextmanager
    async def context():
        func()
        yield

    return context


async def test_iterate_lifespans_empty_list():
    async with iterate_lifespans([]):
        pass


async def test_iterate_lifespans_one_item():
    one = MagicMock()
    async with iterate_lifespans([call_from_context(one)]):  # type: ignore
        pass

    one.assert_called_once()


async def test_iterate_lifespans_three_items():
    mocks = [MagicMock(), MagicMock(), MagicMock()]

    async with iterate_lifespans([call_from_context(x) for x in mocks]):  # type: ignore
        pass

    for mock in mocks:
        mock.assert_called_once()
