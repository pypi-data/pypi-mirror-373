from cattle_grid.testing.fixtures import sql_engine_for_tests  # noqa

from . import lifespan


async def test_lifespan(sql_engine_for_tests):  # noqa
    async with lifespan(sql_engine_for_tests):
        pass
