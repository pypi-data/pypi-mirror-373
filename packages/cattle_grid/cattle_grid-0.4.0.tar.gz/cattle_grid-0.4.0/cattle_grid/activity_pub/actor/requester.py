import logging

from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession
from bovine.activitystreams.utils import recipients_for_object, is_public

from cattle_grid.activity_pub.activity import actor_deletes_themselves
from cattle_grid.database.activity_pub_actor import Actor

from .relationship import followers_for_actor, following_for_actor, is_blocked


logger = logging.getLogger(__name__)


class ActorNotFound(Exception):
    """Raised if an actor is not found"""


async def is_valid_requester(
    session: AsyncSession, requester: str, actor: Actor, obj: dict
):
    """Checks if the requested is allowed to view the object

    FIXME tests in test_actor?
    """

    if await is_blocked(session, actor, requester):
        return False

    if is_public(obj):
        return True

    recipients = recipients_for_object(obj)
    self_delete = actor_deletes_themselves(obj)

    recipients = await update_recipients_for_actor(
        session, actor, recipients, self_delete
    )

    valid_requesters = recipients

    if "actor" in obj:
        valid_requesters = valid_requesters | {obj["actor"]}
    if "attributedTo" in obj:
        valid_requesters = valid_requesters | {obj["attributedTo"]}

    return requester in valid_requesters


async def update_recipients_for_actor(
    session: AsyncSession, actor: Actor, recipients, self_delete=False
):
    """Updates set of recipients by removing the followers and following collections, and replacing
    them with the actual sets.

    The following collecting is only allowed for self delete activities.
    """
    if actor.followers_uri in recipients:
        recipients = recipients - {actor.followers_uri} | set(
            await followers_for_actor(session, actor)
        )

        logger.info("Got recipients %s after handling followers", ", ".join(recipients))

    if actor.following_uri in recipients:
        recipients = recipients - {actor.following_uri}

        if self_delete:
            recipients = recipients | set(await following_for_actor(session, actor))
        else:
            logger.warning(
                "Actor '%s' included following collection in recipients where not allowed",
                actor.actor_id,
            )

    return recipients


async def is_valid_requester_for_obj(session: AsyncSession, requester: str, obj: dict):
    """Checks if the requested is allowed to view the object"""

    actor_id = obj.get("attributedTo")
    if actor_id is None:
        actor_id = obj.get("actor")
    if actor_id is None:
        raise ActorNotFound("Object does not have an actor or attributedTo")

    actor = await session.scalar(select(Actor).where(Actor.actor_id == actor_id))
    if actor is None:
        raise ActorNotFound("Actor not found")

    return await is_valid_requester(session, requester, actor, obj)
