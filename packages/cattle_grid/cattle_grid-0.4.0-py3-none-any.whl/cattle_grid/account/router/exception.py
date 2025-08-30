from faststream.rabbit import RabbitBroker
from faststream import ExceptionMiddleware, Context

import logging

from cattle_grid.model.account import ErrorMessage
from cattle_grid.dependencies import CorrelationId, AccountExchange

from .annotations import AccountName, RoutingKey

logger = logging.getLogger(__name__)

exception_middleware = ExceptionMiddleware()


@exception_middleware.add_handler(Exception)
async def exception_handler(
    exception: Exception,
    name: AccountName,
    routing_key: RoutingKey,
    correlation_id: CorrelationId,
    account_exchange: AccountExchange,
    broker: RabbitBroker = Context(),
):
    logger.error("Processing error occurred for %s", name)
    logger.exception(exception)

    await broker.publish(
        ErrorMessage(message=str(exception), routing_key=routing_key),
        routing_key=f"error.{name}",
        exchange=account_exchange,
        correlation_id=correlation_id,
    )
