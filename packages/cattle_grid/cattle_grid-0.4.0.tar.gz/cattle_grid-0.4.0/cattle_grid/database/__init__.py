from contextlib import asynccontextmanager
import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .auth import Base as AuthBase


logger = logging.getLogger(__name__)

#
# Not sure the following function is what one wants
# ... it means pinning one database migrations work
# ... for
#


@asynccontextmanager
async def database_engine(
    db_uri: str = "sqlite+aiosqlite:///:memory:", echo: bool = False
):
    engine = create_async_engine(db_uri, echo=echo)

    yield engine

    await engine.dispose()


@asynccontextmanager
async def database_session(
    db_uri: str = "sqlite+aiosqlite:///:memory:", echo: bool = False
):
    async with database_engine(db_uri, echo) as engine:
        yield async_sessionmaker(engine)()


async def upgrade_sql_alchemy(sql_engine):
    async with sql_engine.begin() as conn:
        await conn.run_sync(AuthBase.metadata.create_all)


async def run_with_database(config, coro):
    try:
        async with database_session(db_uri=config.db_uri) as session:
            await coro(session)
    except Exception as e:
        logger.exception(e)
