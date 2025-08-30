import asyncio
import logging
from faststream import Context
from faststream.rabbit import RabbitRouter, RabbitBroker, RabbitQueue

from cattle_grid.activity_pub.actor import (
    create_actor,
    actor_to_object,
)

from cattle_grid.model.account import (
    FetchMessage,
    FetchResponse,
    InformationResponse,
    CreateActorRequest,
)
from cattle_grid.account.permissions import can_create_actor_at_base_url
from cattle_grid.database.account import ActorForAccount
from cattle_grid.dependencies import CorrelationId, MethodInformation, SqlSession
from cattle_grid.dependencies.globals import global_container

from .info import create_information_response
from .annotations import (
    AccountName,
    AccountFromRoutingKey,
    ActorFromMessage,
)
from .exception import exception_middleware
from .trigger import handle_trigger

logger = logging.getLogger(__name__)


async def handle_fetch(
    msg: FetchMessage,
    correlation_id: CorrelationId,
    name: AccountName,
    actor: ActorFromMessage,
    broker: RabbitBroker = Context(),
):
    """Used to retrieve an object"""
    try:
        async with asyncio.timeout(0.5):
            result = await broker.publish(
                {"actor": actor.actor_id, "uri": msg.uri},
                routing_key="fetch_object",
                exchange=global_container.internal_exchange,
                rpc=True,
            )
        if result == b"":
            result = None
        logger.info("GOT result %s", result)
    except TimeoutError as e:
        logger.error("Request ran into timeout %s", e)
        result = None

    if result:
        await broker.publish(
            FetchResponse(
                uri=msg.uri,
                actor=actor.actor_id,
                data=result,
            ),
            routing_key=f"receive.{name}.response.fetch",
            exchange=global_container.account_exchange,
            correlation_id=correlation_id,
        )
    else:
        await broker.publish(
            {
                "message": "Could not fetch object",
            },
            routing_key=f"error.{name}",
            exchange=global_container.account_exchange,
            correlation_id=correlation_id,
        )


async def create_actor_handler(
    create_message: CreateActorRequest,
    correlation_id: CorrelationId,
    account: AccountFromRoutingKey,
    session: SqlSession,
    broker: RabbitBroker = Context(),
) -> None:
    """Creates an actor associated with the account.

    Updating and deleting actors is done through trigger events."""

    if not await can_create_actor_at_base_url(
        session, account, create_message.base_url
    ):
        raise ValueError(f"Base URL {create_message.base_url} not in allowed base urls")

    actor = await create_actor(
        session,
        create_message.base_url,
        preferred_username=create_message.preferred_username,
        profile=create_message.profile,
    )

    session.add(
        ActorForAccount(
            account=account,
            actor=actor.actor_id,
            name=create_message.name or "from drive",
        )
    )

    if create_message.automatically_accept_followers:
        actor.automatically_accept_followers = True

    result = actor_to_object(actor)

    await session.refresh(account)

    logger.info("Created actor %s for %s", actor.actor_id, account.name)

    await broker.publish(
        result,
        routing_key=f"receive.{account.name}.response.create_actor",
        exchange=global_container.account_exchange,
        correlation_id=correlation_id,
    )
    await session.commit()


def create_router() -> RabbitRouter:
    router = RabbitRouter(middlewares=[exception_middleware])

    info_publisher = router.publisher(
        "receive.name.response.fetch",
        schema=FetchResponse,
        title="receive.NAME.response.fetch",
    )

    router.subscriber(
        RabbitQueue(
            "send_request_fetch",
            routing_key="send.*.request.fetch",
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.fetch",
    )(handle_fetch)

    info_publisher = router.publisher(
        "receive.name.response.info",
        schema=InformationResponse,
        title="receive.NAME.response.info",
    )

    @router.subscriber(
        RabbitQueue(
            "send_request_info",
            routing_key="send.*.request.info",
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.info",
    )
    async def information_request_handler(
        account: AccountFromRoutingKey,
        correlation_id: CorrelationId,
        method_information: MethodInformation,
        session: SqlSession,
        broker: RabbitBroker = Context(),
    ) -> None:
        """Provides information about the underlying service"""
        await info_publisher.publish(
            await create_information_response(session, account, method_information),
            routing_key=f"receive.{account.name}.response.info",
            exchange=global_container.account_exchange,
            correlation_id=correlation_id,
        )

    info_publisher = router.publisher(
        "receive.name.response.create_actor",
        schema=dict,
        title="receive.NAME.response.create_actor",
        description="""The response to a create_actor request
    is the actor profile (as formatted towards the Fediverse)
    This might change in the future""",
    )

    router.subscriber(
        RabbitQueue(
            "send_request_create_actor",
            routing_key="send.*.request.create_actor",
        ),
        exchange=global_container.account_exchange,
        title="send.*.request.create_actor",
    )(create_actor_handler)

    router.subscriber(
        RabbitQueue(
            "send_trigger",
            routing_key="send.*.trigger.#",
        ),
        exchange=global_container.account_exchange,
        title="send.*.trigger.#",
    )(handle_trigger)

    return router
