from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.dependencies.globals import global_container

from .account import list_permissions
from cattle_grid.database.account import Account


async def allowed_base_urls(session: AsyncSession, account: Account) -> list[str]:
    """Returns the set of base_urls the account
    is allowed to use to create an actor"""
    settings = global_container.config
    await session.refresh(account, attribute_names=["permissions"])

    permissions = list_permissions(account)

    if "admin" in permissions:
        frontend_settings = settings.get("frontend", {})  # type:ignore

        return frontend_settings.get("base_urls", [])

    permission_settings = settings.get("permissions", {})  # type:ignore

    return sum(
        (permission_settings.get(p, {}).get("base_urls", []) for p in permissions),
        [],
    )


async def can_create_actor_at_base_url(
    session: AsyncSession, account: Account, base_url
) -> bool:
    """Checks if the account is allowed to create an actor
    at the base url"""
    allowed_urls = await allowed_base_urls(session, account)

    return base_url in allowed_urls
