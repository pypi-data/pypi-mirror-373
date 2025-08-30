import logging

from typing import Annotated
from faststream import Depends

from bovine import BovineActor

from cattle_grid.dependencies import ClientSession, SqlSession
from cattle_grid.dependencies.processing import actor_id, ProcessingError

from cattle_grid.activity_pub.actor import (
    bovine_actor_for_actor_id,
)

logger = logging.getLogger(__name__)


async def bovine_actor_for_message(
    actor_id: Annotated[str, Depends(actor_id)],
    session: ClientSession,
    sql_session: SqlSession,
) -> BovineActor:
    actor = await bovine_actor_for_actor_id(sql_session, actor_id)
    if actor is None:
        raise ProcessingError("Actor not found")

    await actor.init(session=session)

    return actor


MessageBovineActor = Annotated[BovineActor, Depends(bovine_actor_for_message)]
