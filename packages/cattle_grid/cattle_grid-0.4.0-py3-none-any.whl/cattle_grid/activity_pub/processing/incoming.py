import logging

from faststream import Context
from faststream.rabbit import RabbitRouter
from sqlalchemy import select, delete

from bovine.activitystreams.utils import id_for_object

from cattle_grid.activity_pub.actor import remove_from_followers_following
from cattle_grid.database.activity_pub_actor import Following, Follower
from cattle_grid.model import ActivityMessage
from cattle_grid.model.processing import StoreActivityMessage
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies.processing import MessageActor, FactoriesForActor
from cattle_grid.dependencies import CommittingSession
from .util import actor_deletes_themselves


logger = logging.getLogger(__name__)


async def incoming_follow_request(
    message: ActivityMessage,
    actor: MessageActor,
    factories: FactoriesForActor,
    session: CommittingSession,
    broker=Context(),
):
    """
    For an incoming Follow request an entry in the Follower table is created
    with having `accepted` set to False.

    If the actor automatically accepts followers, the actor sends Accept activity
    to the actor requesting to follow it.
    """
    follow_request = message.data
    to_follow = follow_request.get("object")
    if isinstance(to_follow, dict):
        to_follow = to_follow.get("id")

    if to_follow is None or to_follow != actor.actor_id:
        return

    request_id = follow_request.get("id")
    follower = follow_request.get("actor")

    await session.merge(
        Follower(
            actor=actor,
            follower=follower,
            request=request_id,
            accepted=False,
        )
    )

    if actor.automatically_accept_followers:
        accept = factories[0].accept(follow_request).build()

        await broker.publish(
            StoreActivityMessage(actor=actor.actor_id, data=accept),
            routing_key="store_activity",
            exchange=global_container.internal_exchange,
        )
        logger.info(
            "Got follow request from %s with id %s (auto accepted)",
            follower,
            request_id,
        )

    else:
        logger.info("Got follow request from %s with id %s", follower, request_id)


async def incoming_accept_activity(
    message: ActivityMessage,
    actor: MessageActor,
    session: CommittingSession,
    broker=Context(),
):
    """Handles an incoming Accept activity"""
    accept_request = message.data
    request_being_accepted = id_for_object(accept_request.get("object"))

    following = await session.scalar(
        select(Following).where(Following.request == request_being_accepted)
    )

    if not following:
        logger.warning("Follow request with id '%s' not found", request_being_accepted)
        return

    following.accepted = True
    logger.info("Processed follow request %s (following)", request_being_accepted)


async def incoming_undo_activity(
    message: ActivityMessage,
    actor: MessageActor,
    session: CommittingSession,
    broker=Context(),
):
    """Handles an incoming Undo activity"""

    accept_request = message.data
    request_being_undone = id_for_object(accept_request.get("object"))

    await session.execute(
        delete(Follower).where(Follower.request == request_being_undone)
    )


async def incoming_reject_activity(
    message: ActivityMessage,
    actor: MessageActor,
    session: CommittingSession,
    broker=Context(),
):
    """Handles an incoming Reject activity"""
    reject_request = message.data
    request_being_rejected = reject_request.get("object")

    await session.execute(
        delete(Following).where(Following.request == request_being_rejected)
    )


async def incoming_delete_activity(
    message: ActivityMessage, session: CommittingSession, broker=Context()
):
    if actor_deletes_themselves(message.data):
        actor_id = id_for_object(message.data.get("actor"))
        if actor_id is None:
            return
        logger.info("Got self delete for actor with id '%s'", actor_id)

        await remove_from_followers_following(session, actor_id)


async def incoming_block_activity(
    message: ActivityMessage,
    actor: MessageActor,
    session: CommittingSession,
    broker=Context(),
):
    """Handles an incoming Block activity"""
    current_actor_id = message.data.get("object")
    if current_actor_id != actor.actor_id:
        logger.warning("Mismatch of actor and target of block")
        return

    actor_blocking = message.data.get("actor")

    await session.execute(
        delete(Following).where(Following.following == actor_blocking)
    )


def create_incoming_router(exchange=None):
    router = RabbitRouter()

    if exchange is None:
        exchange = global_container.internal_exchange

    for routing_key, coroutine in [
        ("incoming.Follow", incoming_follow_request),
        ("incoming.Accept", incoming_accept_activity),
        ("incoming.Undo", incoming_undo_activity),
        ("incoming.Delete", incoming_delete_activity),
        ("incoming.Block", incoming_block_activity),
        ("incoming.Reject", incoming_reject_activity),
    ]:
        router.subscriber(
            routing_key,
            exchange=exchange,
            title=routing_key,
        )(coroutine)

    return router
