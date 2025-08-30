"""Dependencies injected by fast_depends"""

import aiohttp
import logging

from typing import Annotated, Callable, Awaitable, Dict, List
from dynaconf import Dynaconf
from fast_depends import Depends
from faststream import Context
from faststream.rabbit import RabbitExchange

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from cattle_grid.model.lookup import LookupMethod
from cattle_grid.model.extension import MethodInformationModel


from .globals import (
    get_transformer,
    get_lookup,
    get_engine,
    get_method_information,
    global_container,
)

logger = logging.getLogger(__name__)


async def get_client_session():
    yield global_container.session


ClientSession = Annotated[aiohttp.ClientSession, Depends(get_client_session)]
"""The [aiohttp.ClientSession][] used by the application"""

Transformer = Annotated[Callable[[Dict], Awaitable[Dict]], Depends(get_transformer)]
"""The transformer loaded from extensions"""

LookupAnnotation = Annotated[LookupMethod, Depends(get_lookup)]
"""The lookup method loaded from extensions"""


InternalExchange = Annotated[
    RabbitExchange, Depends(global_container.get_internal_exchange)
]
"""The interal activity exchange"""


ActivityExchange = Annotated[RabbitExchange, Depends(global_container.get_exchange)]
"""The activity exchange"""

AccountExchange = Annotated[
    RabbitExchange, Depends(global_container.get_account_exchange)
]
"""The account exchange"""

SqlAsyncEngine = Annotated[AsyncEngine, Depends(get_engine)]
"""Returns the SqlAlchemy AsyncEngine"""

CorrelationId = Annotated[str, Context("message.correlation_id")]
"""The correlation id of the message"""

MethodInformation = Annotated[
    List[MethodInformationModel], Depends(get_method_information)
]
"""Returns the information about the methods that are a part of the exchange"""

SqlSessionMaker = Annotated[
    Callable[[], AsyncSession], Depends(global_container.get_session_maker)
]


async def with_sql_session(
    sql_session_maker=Depends(global_container.get_session_maker),
):
    async with sql_session_maker() as session:
        yield session


SqlSession = Annotated[AsyncSession, Depends(with_sql_session)]
"""SQL session that does not commit afterwards"""


async def with_session_commit(session: SqlSession):
    yield session
    await session.commit()


CommittingSession = Annotated[AsyncSession, Depends(with_session_commit)]
"""Session that commits the transaction"""

Config = Annotated[Dynaconf, Depends(global_container.get_config)]
"""Returns the configuration"""
