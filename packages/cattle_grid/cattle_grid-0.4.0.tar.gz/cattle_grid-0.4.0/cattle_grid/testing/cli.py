import pytest
import asyncio

from cattle_grid.database import database_engine


@pytest.fixture
def db_uri(tmp_path):
    return "sqlite+aiosqlite:///" + str(tmp_path / "test.db")


@pytest.fixture
def create_database(db_uri):
    async def run_method():
        async with database_engine(db_uri=db_uri) as engine:
            from cattle_grid.database.activity_pub import Base as APBase

            async with engine.begin() as conn:
                await conn.run_sync(APBase.metadata.create_all)

        await asyncio.sleep(0.3)

    asyncio.run(run_method())
