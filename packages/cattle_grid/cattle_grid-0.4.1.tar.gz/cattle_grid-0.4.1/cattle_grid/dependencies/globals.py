import logging
import re

import aiohttp
from dataclasses import dataclass
from typing import Callable, Awaitable, Dict, List
from contextlib import asynccontextmanager
from functools import cached_property


from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
    AsyncEngine,
)
from dynaconf import Dynaconf
from dynaconf.utils import DynaconfDict

from faststream.rabbit import (
    RabbitBroker,
    RabbitExchange,
    ExchangeType,
)

from cattle_grid.config import load_settings, default_filenames
from cattle_grid.model.lookup import LookupMethod
from cattle_grid.model.extension import MethodInformationModel


logger = logging.getLogger(__name__)


@dataclass
class GlobalContainer:
    session: aiohttp.ClientSession | None = None
    engine: AsyncEngine | None = None
    method_information: List[MethodInformationModel] | None = None

    transformer: Callable[[Dict], Awaitable[Dict]] | None = None
    lookup: LookupMethod | None = None

    _config: Dynaconf | DynaconfDict | None = None

    async_session_maker: Callable[[], AsyncSession] | None = None

    def __post_init__(self):
        self.load_config()

    def get_config(self):
        if self._config is None:
            raise ValueError("Config not loaded")
        return self._config

    @property
    def config(self):
        if self._config is None:
            raise ValueError("Config not loaded")
        return self._config

    def load_config(self, filenames: list[str] = default_filenames):
        self._config = load_settings(filenames)

    @asynccontextmanager
    async def session_lifecycle(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            yield session
            self.session = None

    @asynccontextmanager
    async def alchemy_database(self, db_uri: str | None = None, echo: bool = False):
        """Initializes the sql alchemy engine"""

        if db_uri is None:
            db_uri = self.config.db_uri  # type:ignore

        if db_uri is None:
            raise ValueError("Database URI not set")

        if self.engine or self.async_session_maker:
            raise ValueError("Database already initialized")

        self.engine = create_async_engine(db_uri, echo=echo)
        self.async_session_maker = async_sessionmaker(self.engine)
        logger.debug(
            "Connected to %s with sqlalchemy", re.sub("://.*@", "://***:***@", db_uri)
        )

        yield self.engine

        await self.engine.dispose()
        self.engine = None
        self.async_session_maker = None

    @asynccontextmanager
    async def common_lifecycle(self, config=None):
        if config is None:
            config = self.config

        async with self.session_lifecycle():
            async with self.alchemy_database():
                yield

    @cached_property
    def internal_exchange(self) -> RabbitExchange:
        """The internal exchange used to process
        ActivityPub messages related to the social graph

        :returns:
        """
        return RabbitExchange(
            self.config.activity_pub.internal_exchange,  # type: ignore
            type=ExchangeType.TOPIC,
        )

    def get_internal_exchange(self) -> RabbitExchange:
        return self.internal_exchange

    @cached_property
    def exchange(self) -> RabbitExchange:
        """Returns the public exchange used to process

        :returns:
        """
        return RabbitExchange(
            self.config.activity_pub.exchange,  # type: ignore
            type=ExchangeType.TOPIC,
        )

    def get_exchange(self) -> RabbitExchange:
        return self.exchange

    @cached_property
    def account_exchange(self) -> RabbitExchange:
        """Returns the exchange used to distribute messages between accounts

        :returns:
        """
        exchange_name = self.config.activity_pub.account_exchange  # type: ignore

        durable = True if exchange_name == "amq.topic" else False

        return RabbitExchange(exchange_name, type=ExchangeType.TOPIC, durable=durable)  # type: ignore

    def get_account_exchange(self) -> RabbitExchange:
        return self.account_exchange

    @cached_property
    def broker(self) -> RabbitBroker:
        return RabbitBroker(self.config.amqp_uri)  # type: ignore

    def get_broker(self) -> RabbitBroker:
        return self.broker

    def get_session_maker(self) -> Callable[[], AsyncSession]:
        if not self.async_session_maker:
            raise ValueError("Alchemy database not initialized")
        return self.async_session_maker


global_container = GlobalContainer()


def get_transformer() -> Callable[[Dict], Awaitable[Dict]]:
    global global_container

    if not global_container.transformer:
        raise ValueError("Transformer not initialized")

    return global_container.transformer


def get_lookup() -> LookupMethod:
    global global_container

    if not global_container.lookup:
        raise ValueError("Lookup not initialized")

    return global_container.lookup


def get_engine() -> AsyncEngine:
    global global_container

    if not global_container.engine:
        raise ValueError("Engine not initialized")

    return global_container.engine


def get_method_information() -> List[MethodInformationModel]:
    global global_container

    if global_container.method_information is None:
        raise ValueError("Method information not initialized")

    return global_container.method_information
