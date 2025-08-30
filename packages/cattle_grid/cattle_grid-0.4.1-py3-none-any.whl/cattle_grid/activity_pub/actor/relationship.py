import logging
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.database.activity_pub_actor import Actor, Blocking, Follower, Following

logger = logging.getLogger(__name__)


async def is_blocked(session: AsyncSession, actor: Actor, remote_actor_id: str) -> bool:
    """Checks if remote_actor_id is blocked by actor"""
    result = await session.scalar(
        select(Blocking)
        .where(Blocking.active)
        .where(Blocking.actor == actor)
        .where(Blocking.blocking == remote_actor_id)
        .limit(1)
    )

    return bool(result)


async def followers_for_actor(session: AsyncSession, actor: Actor) -> Sequence[str]:
    """Returns the list of accepted followers

    :param actor:
    :returns:
    """

    result = await session.scalars(
        select(Follower.follower)
        .where(Follower.actor == actor)
        .where(Follower.accepted)
    )

    return result.all()


async def following_for_actor(session: AsyncSession, actor: Actor) -> Sequence[str]:
    """Returns the list of accepted people to follow said actor.
    This is the following table.

    :param actor:
    :returns:
    """

    result = await session.scalars(
        select(Following.following)
        .where(Following.actor == actor)
        .where(Following.accepted)
    )

    return result.all()
