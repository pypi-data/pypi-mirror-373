"""
This extension is an example of storing activities
and then serving them through a HTTP API.

I will possibly extend it to also store objects
(and provide some `Create` activity creation), but
not much more.

A real storage mechanism should have several features
this simple API has not, e.g.

- Serving a HTML page through content negotiation
- Allowing one to update the content of the database
- Collecting and adding metadata, e.g. a replies collection for objects

Usage:

```toml
[[extensions]]
module = "cattle_grid.extensions.examples.simple_storage"
api_prefix = "/simple_storage"

config = { prefix = "/simple_storage/" }
```
"""

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import HTTPException
from faststream import Context
from faststream.rabbit import RabbitBroker
from sqlalchemy.future import select

from bovine.activitystreams import factories_for_actor_object

from cattle_grid.dependencies.globals import global_container
from cattle_grid.dependencies import SqlAsyncEngine, CommittingSession
from cattle_grid.dependencies.fastapi import SqlSession as FastApiSession
from cattle_grid.dependencies.processing import MessageActor

from cattle_grid.extensions import Extension
from cattle_grid.model import ActivityMessage

from cattle_grid.activity_pub.actor import actor_to_object
from cattle_grid.activity_pub.actor.requester import (
    ActorNotFound,
    is_valid_requester_for_obj,
)
from cattle_grid.activity_pub.server.router import ActivityPubHeaders

from .models import StoredActivity, StoredObject, Base
from .message_types import PublishActivity, PublishObject
from .config import SimpleStorageConfiguration

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(engine: SqlAsyncEngine):
    """The lifespan ensure that the necessary database table is
    created."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield


extension = Extension(
    name="simple storage",
    module=__name__,
    lifespan=lifespan,
    config_class=SimpleStorageConfiguration,
)
"""The simple storage extension"""


@extension.subscribe("publish_activity")
async def simple_storage_publish_activity(
    message: PublishActivity,
    config: extension.Config,  # type: ignore
    session: CommittingSession,
    broker: RabbitBroker = Context(),
):
    """Method to subscribe to the `publish_activity` routing_key.

    An activity send to this endpoint will be stored in the
    database, and then published through the `send_message`
    mechanism.

    The stored activity can then be retrieved through the
    HTTP API.
    """
    if message.data.get("id"):
        raise ValueError("Activity ID must not be set")

    if message.data.get("actor") != message.actor:
        raise ValueError("Actor must match message actor")

    activity = message.data
    activity["id"], uuid = config.make_id(message.actor)

    logger.info("Publishing activity with id %s for %s", message.actor, activity["id"])

    session.add(
        StoredActivity(
            id=uuid,
            data=activity,
            actor=message.actor,
        )
    )

    await broker.publish(
        ActivityMessage(actor=message.actor, data=activity),
        routing_key="send_message",
        exchange=global_container.exchange,
    )


@extension.subscribe("publish_object")
async def simple_storage_publish_object(
    message: PublishObject,
    config: extension.Config,  # type: ignore
    session: CommittingSession,
    actor: MessageActor,
    broker: RabbitBroker = Context(),
):
    """Publishes an object, subscribed to the routing key
    `publish_object`.

    We note that this routine creates a `Create` activity for the object."""

    if message.data.get("id"):
        raise ValueError("Object ID must not be set")

    if message.data.get("attributedTo") != message.actor:
        raise ValueError("Actor must match object attributedTo")

    obj = message.data
    obj["id"], obj_uuid = config.make_id(message.actor)

    logger.info("Publishing object with id %s for %s", message.actor, obj["id"])

    actor_profile = actor_to_object(actor)
    activity_factory, _ = factories_for_actor_object(actor_profile)

    activity_id, activity_uuid = config.make_id(message.actor)

    activity = activity_factory.create(obj, id=activity_id).build()

    logger.info(activity)

    await broker.publish(
        ActivityMessage(actor=message.actor, data=activity),
        routing_key="send_message",
        exchange=global_container.exchange,
    )

    session.add(
        StoredActivity(
            id=activity_uuid,
            data=activity,
            actor=message.actor,
        )
    )
    session.add(
        StoredObject(
            id=obj_uuid,
            data=obj,
            actor=message.actor,
        )
    )


@extension.get("/")
async def main():
    """Basic endpoint that just returns a string, so
    requesting with an uuid doesn't return an error."""
    return "simple storage cattle grid sample extension"


@extension.get("/{uuid}")
async def get_activity_or_object(
    uuid: uuid.UUID, headers: ActivityPubHeaders, session: FastApiSession
):
    """Returns the activity or object"""
    result = await session.scalar(
        select(StoredActivity).where(StoredActivity.id == uuid)
    )

    if result is None:
        result = await session.scalar(
            select(StoredObject).where(StoredObject.id == uuid)
        )

    if result is None:
        raise HTTPException(status_code=404, detail="Activity not found")

    try:
        if not await is_valid_requester_for_obj(
            session, headers.x_cattle_grid_requester, result.data
        ):
            raise HTTPException(status_code=401)
    except ActorNotFound:
        raise HTTPException(status_code=410, detail="Activity no longer available")

    if result.data.get("id") != headers.x_ap_location:
        raise HTTPException(status_code=400, detail="Location header does not match id")

    return result.data
