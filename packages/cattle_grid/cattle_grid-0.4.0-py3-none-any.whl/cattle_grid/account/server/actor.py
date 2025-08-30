from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from cattle_grid.model import FetchMessage
from cattle_grid.dependencies.fastapi import (
    Transformer,
    Broker,
    InternalExchange,
    ActivityExchange,
    SqlSession,
)

from .dependencies import CurrentAccount
from .responses import (
    LookupRequest,
)
from .responses import PerformRequest

from cattle_grid.database.account import Account, ActorForAccount


actor_router = APIRouter(prefix="/actor", tags=["actor"])


async def actor_from_account(
    session: AsyncSession, account: Account, actor_id: str
) -> ActorForAccount | None:
    await session.refresh(account, attribute_names=["actors"])

    for actor in account.actors:
        if actor.actor == actor_id:
            return actor
    return None


@actor_router.post("/lookup", response_model_exclude_none=True, operation_id="lookup")
async def lookup(
    body: LookupRequest,
    account: CurrentAccount,
    broker: Broker,
    exchange: InternalExchange,
    transformer: Transformer,
    session: SqlSession,
) -> dict:
    """Looks up the resource given by `uri` as the actor with
    actor id `actor_id`. Here looking up the actor means that
    the request is signed using a private key belonging to that actor."""

    actor = await actor_from_account(session, account, body.actor_id)
    if actor is None:
        raise HTTPException(400)

    msg = FetchMessage(actor=actor.actor, uri=body.uri)

    result = await broker.publish(
        msg, routing_key="fetch_object", exchange=exchange, rpc=True
    )

    if result is None:
        return {"raw": {}}

    return await transformer({"raw": result})


@actor_router.post("/trigger/{method}", status_code=202, operation_id="trigger")
async def trigger_action(
    method: str,
    body: PerformRequest,
    account: CurrentAccount,
    broker: Broker,
    exchange: ActivityExchange,
    session: SqlSession,
):
    """This method allows one to trigger asynchronous activities
    through a synchronous request. The basic result is that
    the data is posted to the ActivityExchange with the
    routing_key specified.

    """

    actor = await actor_from_account(session, account, body.actor)

    if actor is None:
        raise HTTPException(400)

    await broker.publish(
        body.model_dump(),
        routing_key=method,
        exchange=exchange,
    )
