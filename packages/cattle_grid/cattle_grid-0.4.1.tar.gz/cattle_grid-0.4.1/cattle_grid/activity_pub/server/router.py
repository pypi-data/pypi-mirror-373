"""ActivityPub related functionality"""

import logging
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from typing import Annotated
from bovine.activitystreams import OrderedCollection
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from cattle_grid.database.activity_pub_actor import Actor, ActorStatus
from cattle_grid.dependencies.fastapi import SqlSession

from cattle_grid.activity_pub.actor import (
    actor_to_object,
)
from cattle_grid.activity_pub.actor.relationship import (
    is_blocked,
    followers_for_actor,
    following_for_actor,
)

logger = logging.getLogger(__name__)

ap_router = APIRouter()


class APHeaders(BaseModel):
    """Headers every request should have. These should be added by the remote proxy."""

    x_cattle_grid_requester: str
    """URI of the actor making the request"""
    x_ap_location: str
    """URI of the resource being retrieved"""


ActivityPubHeaders = Annotated[APHeaders, Header()]


class ActivityResponse(JSONResponse):
    """Response that ensures the content-type is
    "application/activity+json"
    """

    media_type = "application/activity+json"


def validate_actor(actor: Actor | None) -> Actor:
    if actor is None:
        raise HTTPException(404)
    if actor.status == ActorStatus.deleted:
        raise HTTPException(410)

    return actor


@ap_router.get("/actor/{id_str}", response_class=ActivityResponse)
async def actor_profile(id_str, headers: ActivityPubHeaders, session: SqlSession):
    """Returns the actor"""
    logger.debug("Request for actor at %s", headers.x_ap_location)
    actor = await session.scalar(
        select(Actor)
        .where(Actor.actor_id == headers.x_ap_location)
        .options(joinedload(Actor.identifiers))
    )
    actor = validate_actor(actor)

    if await is_blocked(session, actor, headers.x_cattle_grid_requester):
        raise HTTPException(403)

    result = actor_to_object(actor)
    return result


@ap_router.get("/outbox/{id_str}", response_class=ActivityResponse)
async def outbox(id_str, headers: ActivityPubHeaders, session: SqlSession):
    """Returns an empty ordered collection as outbox"""
    actor = await session.scalar(
        select(Actor).where(Actor.outbox_uri == headers.x_ap_location)
    )
    actor = validate_actor(actor)

    if await is_blocked(session, actor, headers.x_cattle_grid_requester):
        raise HTTPException(403)

    return OrderedCollection(id=headers.x_ap_location).build()


@ap_router.get("/following/{id_str}", response_class=ActivityResponse)
async def following(id_str, headers: ActivityPubHeaders, session: SqlSession):
    """Returns the following"""

    actor = await session.scalar(
        select(Actor).where(Actor.following_uri == headers.x_ap_location)
    )
    actor = validate_actor(actor)

    if await is_blocked(session, actor, headers.x_cattle_grid_requester):
        raise HTTPException(403)
    following = await following_for_actor(session, actor)
    return OrderedCollection(id=headers.x_ap_location, items=following).build()


@ap_router.get("/followers/{id_str}", response_class=ActivityResponse)
async def followers(id_str, headers: ActivityPubHeaders, session: SqlSession):
    """Returns the followers"""
    actor = await session.scalar(
        select(Actor).where(Actor.followers_uri == headers.x_ap_location)
    )
    actor = validate_actor(actor)

    if await is_blocked(session, actor, headers.x_cattle_grid_requester):
        raise HTTPException(403)
    followers = await followers_for_actor(session, actor)
    return OrderedCollection(id=headers.x_ap_location, items=followers).build()
