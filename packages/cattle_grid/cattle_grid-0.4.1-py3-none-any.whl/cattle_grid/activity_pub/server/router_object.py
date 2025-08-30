"""ActivityPub related functionality"""

import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from cattle_grid.database.activity_pub_actor import StoredActivity
from cattle_grid.activity_pub.actor.requester import is_valid_requester
from cattle_grid.dependencies.fastapi import SqlSession

from .router import ActivityPubHeaders, ActivityResponse

logger = logging.getLogger(__name__)

ap_router_object = APIRouter()


@ap_router_object.get("/object/{obj_id}", response_class=ActivityResponse)
async def return_object(obj_id, headers: ActivityPubHeaders, session: SqlSession):
    """Returns the stored activities"""

    obj = await session.scalar(
        select(StoredActivity).where(StoredActivity.id == obj_id)
    )
    if obj is None or not isinstance(obj.data, dict):
        raise HTTPException(404)

    if obj.data.get("id") != headers.x_ap_location:
        raise HTTPException(404)

    if not await is_valid_requester(
        session, headers.x_cattle_grid_requester, obj.actor, obj.data
    ):
        raise HTTPException(401)

    return obj.data
