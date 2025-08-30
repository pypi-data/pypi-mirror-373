"""ActivityPub related functionality"""

import logging
import json
from fastapi import APIRouter, HTTPException, Header, Request
from typing import Annotated
from bovine.crypto.digest import validate_digest
from sqlalchemy import select

from cattle_grid.database.activity_pub_actor import Actor
from cattle_grid.activity_pub.enqueuer import (
    enqueue_from_inbox,
    enqueue_from_shared_inbox,
)

from cattle_grid.dependencies.fastapi import Broker, InternalExchange, SqlSession

from .router import APHeaders

logger = logging.getLogger(__name__)

ap_router_inbox = APIRouter()


class APHeadersWithDigest(APHeaders):
    """The addition of digest headers"""

    digest: str | None = None
    """Legacy digest"""
    content_digest: str | None = None
    """Digest according to [RFC 9530 Digest Fields](https://www.rfc-editor.org/rfc/rfc9530.html)"""


def validate_digest_header(headers: APHeadersWithDigest, data: bytes):
    digest_headers = {}
    if headers.digest:
        digest_headers["digest"] = headers.digest
    if headers.content_digest:
        digest_headers["content-digest"] = headers.content_digest

    if not validate_digest(digest_headers, data):
        raise HTTPException(400)


def parse_body(raw_body: bytes) -> dict:
    data = json.loads(raw_body)
    if not isinstance(data, dict):
        logger.info("Could not parse request body")
        logger.debug(data)
        raise HTTPException(422)

    return data


@ap_router_inbox.post("/inbox/{id_str}", status_code=202)
async def inbox(
    id_str,
    request: Request,
    headers: Annotated[APHeadersWithDigest, Header()],
    broker: Broker,
    exchange: InternalExchange,
    session: SqlSession,
):
    """Processes an inbox message"""
    logger.info("Got incoming request")
    actor = await session.scalar(
        select(Actor).where(Actor.inbox_uri == headers.x_ap_location)
    )
    if actor is None:
        raise HTTPException(404)

    try:
        raw_body = await request.body()
        validate_digest_header(headers, raw_body)
        data = parse_body(raw_body)

        request_actor = data.get("actor")

        if request_actor != headers.x_cattle_grid_requester:
            raise HTTPException(401)

        await enqueue_from_inbox(broker, exchange, actor.actor_id, data)

        return ""

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("Processing post request failed with %s", e)
        logger.exception(e)

        raise HTTPException(422)


@ap_router_inbox.post("/shared_inbox", status_code=202)
async def shared_inbox(
    request: Request,
    headers: Annotated[APHeadersWithDigest, Header()],
    broker: Broker,
    exchange: InternalExchange,
):
    try:
        raw_body = await request.body()
        validate_digest_header(headers, raw_body)
        data = parse_body(raw_body)

        request_actor = data.get("actor")

        if request_actor != headers.x_cattle_grid_requester:
            raise HTTPException(401)

        await enqueue_from_shared_inbox(broker, exchange, data)

        return ""

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error("Processing post request failed with %s", e)
        logger.exception(e)

        raise HTTPException(422)
