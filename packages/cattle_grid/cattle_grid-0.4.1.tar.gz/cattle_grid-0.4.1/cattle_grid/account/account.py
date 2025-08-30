import argon2
import logging
import re

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.config.settings import get_settings
from cattle_grid.database.activity_pub_actor import Actor

from cattle_grid.database.account import (
    Account,
    Permission,
    ActorStatus,
    ActorForAccount,
    ActorGroup,
)

logger = logging.getLogger(__name__)

password_hasher = argon2.PasswordHasher()


class AccountAlreadyExists(Exception):
    pass


class InvalidAccountName(Exception):
    pass


class WrongPassword(Exception):
    pass


async def create_account(
    session: AsyncSession,
    name: str,
    password: str,
    settings=get_settings(),
    permissions: list[str] = [],
    meta_information: dict[str, str] = {},
) -> Account | None:
    """Creates a new account for name and password"""
    if await session.scalar(select(Account).where(Account.name == name)):
        raise AccountAlreadyExists("Account already exists")

    if not re.match(settings.account.allowed_name_regex, name):  # type: ignore
        raise InvalidAccountName("Account name does not match allowed format")

    if name in settings.account.forbidden_names:  # type: ignore
        raise InvalidAccountName("Account name is forbidden")

    account = Account(
        name=name,
        password_hash=password_hasher.hash(password),
        meta_information=meta_information,
    )
    session.add(account)
    await session.commit()

    for permission in permissions:
        await add_permission(session, account, permission)
    return account


async def account_with_name_password(
    session: AsyncSession, name: str, password: str
) -> Account | None:
    """Retrieves account for given name and password"""
    account = await session.scalar(select(Account).where(Account.name == name))
    if account is None:
        return None

    try:
        password_hasher.verify(account.password_hash, password)
    except argon2.exceptions.VerifyMismatchError:
        logger.warning("Got wrong password for %s", name)
        return None

    # Implement rehash?
    # https://argon2-cffi.readthedocs.io/en/stable/howto.html

    return account


async def delete_account(
    session: AsyncSession, name: str, password: str | None = None, force: bool = False
) -> None:
    """Deletes account for given account name and password

    If password is wrong or account does not exist,
    raises a WrongPassword exception"""
    if force:
        account = await session.scalar(select(Account).where(Account.name == name))
    else:
        if not password:
            raise ValueError("Password must be provided if not forcing deletion")
        account = await account_with_name_password(session, name, password)

    if account is None:
        raise WrongPassword(
            "Either the account does not exist or the password is wrong"
        )

    await session.refresh(account, attribute_names=["actors"])

    active_actors = [a for a in account.actors if a.status == ActorStatus.active]
    if len(active_actors) > 0:
        logger.warning(
            "Deleting account with active actors: %s", [a.actor for a in active_actors]
        )

    await session.delete(account)
    await session.commit()


async def add_permission(
    session: AsyncSession, account: Account, permission: str
) -> None:
    """Adds permission to account"""
    session.add(Permission(account=account, name=permission))
    await session.commit()


async def remove_permission(
    session: AsyncSession, account: Account, permission: str
) -> None:
    """Removes permission from account"""
    await session.execute(
        delete(Permission)
        .where(Permission.account == account)
        .where(Permission.name == permission)
    )


def list_permissions(account: Account) -> list[str]:
    """Returns list of permissions for account"""
    return [p.name for p in account.permissions]


async def account_for_actor(session: AsyncSession, actor: str) -> Account | None:
    """Given an actor_id returns the corresponding account or None"""
    actor_for_account = await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == actor)
    )

    if not actor_for_account:
        return None

    return actor_for_account.account


async def add_actor_to_account(
    session: AsyncSession, account: Account, actor: Actor, name: str = "added"
) -> None:
    """Adds the actor to the account"""
    session.add(ActorForAccount(account=account, actor=actor.actor_id, name=name))
    await session.commit()


async def add_actor_to_group(
    session: AsyncSession, actor: ActorForAccount, group_name: str
) -> None:
    """Adds the actor to the group"""
    session.add(ActorGroup(actor=actor, name=group_name))
    await session.commit()


async def group_names_for_actor(
    session: AsyncSession, actor: ActorForAccount
) -> list[str]:
    """Returns the group names for an actor"""
    await session.refresh(actor, attribute_names=["groups"])
    return [g.name for g in actor.groups]


async def actor_for_actor_id(
    session: AsyncSession, actor_id: str
) -> ActorForAccount | None:
    """Returns the ActorForAccount for the given actor_id"""
    return await session.scalar(
        select(ActorForAccount).where(ActorForAccount.actor == actor_id)
    )
