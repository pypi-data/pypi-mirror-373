import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faststream.rabbit import RabbitQueue
from typing import Set

from cattle_grid.activity_pub.actor.requester import update_recipients_for_actor
from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.activity_pub.activity import actor_deletes_themselves
from cattle_grid.model import ActivityMessage

logger = logging.getLogger(__name__)


def queue_for_routing_key(routing_key):
    return RabbitQueue(f"processing_{routing_key}", routing_key=routing_key)


async def update_recipients_for_collections(
    session: AsyncSession, msg: ActivityMessage, recipients: Set[str]
) -> Set[str]:
    """Updates recipients with followers and following collection."""

    db_actor = await session.scalar(select(Actor).where(Actor.actor_id == msg.actor))

    if db_actor is None:
        raise ValueError("Actor not found")

    self_delete = actor_deletes_themselves(msg.data)

    return await update_recipients_for_actor(
        session, db_actor, recipients, self_delete=self_delete
    )
