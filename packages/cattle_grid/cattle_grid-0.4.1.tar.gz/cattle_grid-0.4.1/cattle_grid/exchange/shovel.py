import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from faststream import Context
from faststream.rabbit import RabbitBroker

from bovine.activitystreams.utils import id_for_object

from cattle_grid.model import ActivityMessage as RawActivityMessage
from cattle_grid.database.activity_pub_actor import Actor, Blocking

from cattle_grid.dependencies import Transformer, CorrelationId, SqlSession
from cattle_grid.dependencies.globals import global_container

from cattle_grid.database.account import ActorForAccount

from cattle_grid.model.account import EventInformation, EventType

logger = logging.getLogger(__name__)


async def should_shovel_activity(session: AsyncSession, activity: dict) -> bool:
    """Some activities like Block or Undo Block should not be visible to the user. This method
    returns False if this is the case."""

    activity_type = activity.get("type")

    if activity_type == "Block":
        return False

    if activity_type == "Undo":
        object_id = id_for_object(activity.get("object"))
        blocking = await session.scalar(
            func.count(
                select(Blocking.id)
                .where(Blocking.request == object_id)
                .scalar_subquery()
            )
        )

        if blocking:
            return False

    return True


async def shovel_to_account_exchange(
    actor: str,
    account_name: str,
    event_type: EventType,
    to_shovel: dict,
    broker: RabbitBroker,
    correlation_id: str,
):
    await broker.publish(
        EventInformation(
            actor=actor,
            event_type=event_type,
            data=to_shovel,
        ),
        routing_key=f"receive.{account_name}.{event_type.value}",
        exchange=global_container.account_exchange,
        correlation_id=correlation_id,
    )


async def incoming_shovel(
    msg: RawActivityMessage,
    transformer: Transformer,
    correlation_id: CorrelationId,
    session: SqlSession,
    broker: RabbitBroker = Context(),
) -> None:
    """Transfers the message from the RawExchange to the
    Activity- and Account one.

    The message is passed through the transformer.
    """
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == msg.actor)
    )

    if actor_for_account is None:
        logger.warning("Got actor without account %s", msg.actor)
        return

    activity = msg.data

    if not await should_shovel_activity(session, activity):
        return

    # FIXME: Use join to combine the next two queries ...

    db_actor = await session.scalar(select(Actor).where(Actor.actor_id == msg.actor))
    if not db_actor:
        raise ValueError("Actor not found in database")

    blocking = await session.scalar(
        select(Blocking)
        .where(Blocking.actor == db_actor)
        .where(Blocking.blocking == activity.get("actor"))
        .where(Blocking.active)
    )
    if blocking:
        return

    account_name = actor_for_account.account.name
    to_shovel = await transformer({"raw": msg.data})
    activity_type = msg.data.get("type")

    await shovel_to_account_exchange(
        msg.actor, account_name, EventType.incoming, to_shovel, broker, correlation_id
    )

    await broker.publish(
        {
            "actor": msg.actor,
            "data": to_shovel,
        },
        routing_key=f"incoming.{activity_type}",
        exchange=global_container.exchange,
        correlation_id=correlation_id,
    )


async def outgoing_shovel(
    msg: RawActivityMessage,
    transformer: Transformer,
    correlation_id: CorrelationId,
    session: SqlSession,
    broker: RabbitBroker = Context(),
) -> None:
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == msg.actor)
    )

    logger.debug("OUTGOING SHOVEL")

    if actor_for_account is None:
        logger.warning("Actor %s for account not found", msg.actor)
        return

    account_name = actor_for_account.account.name
    to_shovel = await transformer({"raw": msg.data})
    activity_type = msg.data.get("type")

    await shovel_to_account_exchange(
        msg.actor, account_name, EventType.outgoing, to_shovel, broker, correlation_id
    )

    await broker.publish(
        {
            "actor": msg.actor,
            "data": to_shovel,
        },
        routing_key=f"outgoing.{activity_type}",
        exchange=global_container.exchange,
        correlation_id=correlation_id,
    )
