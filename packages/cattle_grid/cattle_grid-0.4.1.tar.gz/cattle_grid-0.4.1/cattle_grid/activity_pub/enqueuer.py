from faststream.rabbit import RabbitBroker, RabbitExchange
from cattle_grid.model import ActivityMessage, SharedInboxMessage


def determine_activity_type(activity: dict) -> str | None:
    """Determines the type of an activity

    ```pycon
    >>> determine_activity_type({"type": "Follow"})
    'Follow'

    ```


    ```pycon
    >>> determine_activity_type({}) is None
    True

    ```

    In the case of multiple types, these are concatenated. This means
    that they are probably missed by processing, but don't get ignored.

    ```pycon
    >>> determine_activity_type({"type": ["Follow", "WhileSkipping"]})
    'FollowWhileSkipping'

    ```

    :params activity:
    :returns:

    """

    activity_type = activity.get("type")
    if activity_type is None:
        return None
    if isinstance(activity_type, list):
        activity_type = "".join(activity_type)

    return activity_type


async def enqueue_from_inbox(
    broker: RabbitBroker,
    exchange: RabbitExchange,
    receiving_actor_id: str,
    content: dict,
):
    """Enqueues a new message arrived from the inbox

    The routing key will be `incoming.${activity_type}`
    """
    activity_type = determine_activity_type(content)
    if activity_type is None:
        return

    msg = ActivityMessage(actor=receiving_actor_id, data=content)

    await broker.publish(
        msg, exchange=exchange, routing_key=f"incoming.{activity_type}"
    )


async def enqueue_from_shared_inbox(
    broker: RabbitBroker,
    exchange: RabbitExchange,
    content: dict,
):
    """Enqueues a new message arrived from the inbox

    The routing key will be `incoming.${activity_type}`
    """
    activity_type = determine_activity_type(content)
    if activity_type is None:
        return

    msg = SharedInboxMessage(data=content)

    await broker.publish(msg, exchange=exchange, routing_key="shared_inbox")
