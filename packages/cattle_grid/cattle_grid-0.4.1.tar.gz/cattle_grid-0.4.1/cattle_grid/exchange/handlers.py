import logging

from typing import Annotated
from faststream import Context
from faststream.rabbit import RabbitBroker
from sqlalchemy import select
from sqlalchemy.orm.attributes import flag_modified

from cattle_grid.activity_pub.actor import (
    update_for_actor_profile,
    delete_actor,
    delete_for_actor_profile,
)
from cattle_grid.database.account import ActorForAccount, ActorStatus
from cattle_grid.dependencies import SqlSession
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies.processing import MessageActor

from cattle_grid.model.exchange import (
    UpdateActorMessage,
    DeleteActorMessage,
)
from cattle_grid.model.processing import StoreActivityMessage

from .actor_update import handle_actor_action

logger = logging.getLogger(__name__)


async def update_actor(
    message: UpdateActorMessage,
    actor: MessageActor,
    session: SqlSession,
    broker: RabbitBroker = Context(),
) -> None:
    """Should be used asynchronously"""
    send_update = False

    for action in message.actions:
        try:
            if await handle_actor_action(actor, session, action):
                await session.refresh(actor, attribute_names=["identifiers"])
                send_update = True
        except Exception as e:
            logger.error(
                "Something went wrong when handling action of type %s",
                action.action.value,
            )
            logger.exception(e)

            # FIXME publish to error? How?

    if message.profile:
        actor.profile.update(message.profile)
        flag_modified(actor, "profile")

        logger.info("Updating actor %s", actor.actor_id)
        await session.commit()

        send_update = True

    if message.autoFollow is not None:
        actor.automatically_accept_followers = message.autoFollow
        await session.commit()

    await session.refresh(actor)

    if send_update:
        await broker.publish(
            StoreActivityMessage(
                actor=message.actor, data=update_for_actor_profile(actor)
            ),
            routing_key="store_activity",
            exchange=global_container.internal_exchange,
        )


async def delete_actor_handler(
    message: DeleteActorMessage,
    actor: MessageActor,
    session: SqlSession,
    broker: Annotated[RabbitBroker, Context()],
) -> None:
    """
    Deletes the actor by id. Should be used asynchronously.

    """

    logger.info("Deleting actor %s", message.actor)
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == message.actor)
    )
    if actor_for_account:
        logger.info("setting account to deleted")
        actor_for_account.status = ActorStatus.deleted

    await session.refresh(actor, attribute_names=["identifiers"])

    await broker.publish(
        StoreActivityMessage(
            actor=actor.actor_id, data=delete_for_actor_profile(actor)
        ),
        routing_key="store_activity",
        exchange=global_container.internal_exchange,
    )

    await delete_actor(session, actor)
    await session.commit()
