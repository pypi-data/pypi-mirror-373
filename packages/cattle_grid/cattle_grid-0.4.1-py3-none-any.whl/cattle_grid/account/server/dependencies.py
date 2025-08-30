from sqlalchemy import select
from typing import Annotated

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

# from cattle_grid.account.models import AuthenticationToken, Account
from cattle_grid.dependencies.fastapi import SqlSession
from cattle_grid.database.account import Account, AuthenticationToken


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/signin")


async def get_current_account(
    session: SqlSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> Account:
    from_db = await session.scalar(
        select(AuthenticationToken).where(AuthenticationToken.token == token)
    )

    if from_db is None:
        raise HTTPException(401)

    return from_db.account


CurrentAccount = Annotated[Account, Depends(get_current_account)]
"""Annotation for the current account"""
