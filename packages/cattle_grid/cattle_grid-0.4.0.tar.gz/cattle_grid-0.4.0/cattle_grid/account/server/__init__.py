import logging

from uuid import uuid4
from fastapi import APIRouter, HTTPException


from cattle_grid.database.account import AuthenticationToken
from cattle_grid.account.account import account_with_name_password
from cattle_grid.dependencies.fastapi import CommittingSqlSession

from .responses import TokenResponse, SignInData
from .actor import actor_router
from .account import account_router

logger = logging.getLogger(__name__)


router = APIRouter()
router.include_router(actor_router)
router.include_router(account_router)


@router.post("/signin", operation_id="signin")
async def signin(data: SignInData, session: CommittingSqlSession) -> TokenResponse:
    """Allows one to sign in to an account on cattle_grid.
    The response a token to be included using bearer authentication."""
    account = await account_with_name_password(session, data.name, data.password)
    if account is None:
        raise HTTPException(401)

    token = str(uuid4())
    session.add(AuthenticationToken(account=account, token=token))

    return TokenResponse(token=token)
