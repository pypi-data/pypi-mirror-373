import aiohttp

from typing import Annotated, Callable, Awaitable, Dict, List
from dynaconf import Dynaconf
from faststream.rabbit import RabbitBroker, RabbitExchange

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from fastapi import Depends

from cattle_grid.model.extension import MethodInformationModel
from .globals import (
    get_engine,
    get_transformer,
    get_method_information,
    global_container,
)

SqlAsyncEngine = Annotated[AsyncEngine, Depends(get_engine)]
"""Returns the SqlAlchemy AsyncEngine"""

Transformer = Annotated[Callable[[Dict], Awaitable[Dict]], Depends(get_transformer)]
"""The transformer loaded from extensions"""

Broker = Annotated[RabbitBroker, Depends(global_container.get_broker)]
"""The RabbitMQ broker"""
InternalExchange = Annotated[
    RabbitExchange, Depends(global_container.get_internal_exchange)
]

ActivityExchange = Annotated[RabbitExchange, Depends(global_container.get_exchange)]
"""The Activity Exchange"""


MethodInformation = Annotated[
    List[MethodInformationModel], Depends(get_method_information)
]
"""Returns the information about the methods that are a part of the exchange"""


async def with_fast_api_session(sql_engine: SqlAsyncEngine):
    async with async_sessionmaker(sql_engine)() as session:
        yield session


SqlSession = Annotated[AsyncSession, Depends(with_fast_api_session)]
"""Session annotation to be used with FastAPI"""


async def with_committing_sql_session(session: SqlSession):
    yield session
    await session.commit()


CommittingSqlSession = Annotated[AsyncSession, Depends(with_committing_sql_session)]
"""Session annotation to be used with FastAPI. A commit is performed, after processing the request"""


Config = Annotated[Dynaconf, Depends(global_container.get_config)]
"""Returns the configuration"""


async def get_client_session():
    yield global_container.session


ClientSession = Annotated[aiohttp.ClientSession, Depends(get_client_session)]
"""The [aiohttp.ClientSession][] used by the application"""
