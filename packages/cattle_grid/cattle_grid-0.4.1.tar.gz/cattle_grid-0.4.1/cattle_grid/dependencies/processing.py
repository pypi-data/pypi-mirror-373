import logging

from typing import Annotated
from faststream import Depends

from bovine.activitystreams import factories_for_actor_object
from bovine.activitystreams.activity_factory import ActivityFactory
from bovine.activitystreams.object_factory import ObjectFactory
from sqlalchemy import select


from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.dependencies import SqlSession
from cattle_grid.model.common import WithActor


logger = logging.getLogger(__name__)


class ProcessingError(ValueError): ...


async def actor_id(message: WithActor) -> str:
    return message.actor


async def actor_for_message(session: SqlSession, actor_id: str = Depends(actor_id)):
    actor = await session.scalar(select(Actor).where(Actor.actor_id == actor_id))

    if actor is None:
        raise ProcessingError("Actor not found")

    return actor


MessageActor = Annotated[Actor, Depends(actor_for_message)]
"""Returns the actor for the message"""


def get_actor_profile(actor: MessageActor):
    return actor_to_object(actor)


ActorProfile = Annotated[dict, Depends(get_actor_profile)]
"""Returns the actor profile of the actor processing the
message"""


def get_factories_for_actor(profile: ActorProfile):
    return factories_for_actor_object(profile)


FactoriesForActor = Annotated[
    tuple[ActivityFactory, ObjectFactory], Depends(get_factories_for_actor)
]
"""Returns the activity and object factories for the actor"""
