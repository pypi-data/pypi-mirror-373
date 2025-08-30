import logging

from bovine import BovineActor
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.database.activity_pub import InboxLocation
from cattle_grid.model import FetchMessage

from cattle_grid.dependencies import LookupAnnotation, SqlSession
from cattle_grid.model.lookup import Lookup

from cattle_grid.model.processing import ToSendMessage
from .common import MessageBovineActor


logger = logging.getLogger(__name__)


async def fetch_object(
    message: FetchMessage,
    actor: MessageBovineActor,
    lookup: LookupAnnotation,
):
    """Handles retrieving a remote object"""

    try:
        lookup_result = await lookup(Lookup(uri=message.uri, actor=message.actor))
        if lookup_result.result:
            return lookup_result.result
    except Exception as e:
        logger.error("Something went up with lookup")
        logger.exception(e)

        lookup_result = Lookup(uri=message.uri, actor=message.actor)

    result = await actor.get(lookup_result.uri, fail_silently=True)

    return result


async def resolve_inbox(session: AsyncSession, actor: BovineActor, target: str):
    """Resolves the inbox of target for actor using
    a cache"""
    cached = await session.scalar(
        select(InboxLocation).where(InboxLocation.actor == target)
    )

    if cached:
        return cached.inbox

    target_actor = await actor.get(target)
    if not target_actor:
        return None

    inbox = target_actor.get("inbox")
    if inbox is None:
        return

    session.add(InboxLocation(actor=target, inbox=inbox))

    try:
        await session.commit()
    except IntegrityError:
        ...
    return inbox


async def sending_message(
    message: ToSendMessage, actor: MessageBovineActor, sql_session: SqlSession
):
    """Handles sending a message"""
    inbox = await resolve_inbox(sql_session, actor, message.target)
    if inbox:
        result = await actor.post(inbox, message.data)
        logger.info("Got %s for sending to %s", str(result), inbox)
