from faststream import Context
from faststream.rabbit import RabbitBroker
from sqlalchemy import select


from bovine.activitystreams.utils import recipients_for_object

from cattle_grid.model import SharedInboxMessage
from cattle_grid.database.activity_pub_actor import Actor, Following
from cattle_grid.activity_pub.enqueuer import enqueue_from_inbox
from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies import SqlSession


def to_result_set(result):
    return set(result.all())


async def handle_shared_inbox_message(
    message: SharedInboxMessage,
    session: SqlSession,
    broker: RabbitBroker = Context(),
):
    """
    This method is used to handle incoming messages from the shared inbox.
    """

    recipients = recipients_for_object(message.data)
    sender = message.data.get("actor")

    if sender is None:
        return

    local_actor_ids = to_result_set(
        await session.scalars(
            select(Actor.actor_id).where(Actor.actor_id.in_(recipients))
        )
    )
    following_actor_ids = {
        x.actor.actor_id
        for x in await session.scalars(
            select(Following)
            .where(Following.following == sender)
            .where(Following.accepted)
        )
    }

    for actor in local_actor_ids | following_actor_ids:
        await enqueue_from_inbox(
            broker, global_container.internal_exchange, actor, message.data
        )
