import logging
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession

from cattle_grid.model.exchange import UpdateIdentifierAction
from cattle_grid.database.activity_pub_actor import (
    Actor,
    PublicIdentifier,
    PublicIdentifierStatus,
)
from cattle_grid.account.account import account_for_actor
from cattle_grid.account.permissions import allowed_base_urls
from cattle_grid.dependencies.globals import global_container


def get_base_urls() -> list[str]:
    return global_container.config.get("frontend", {}).get(  # type:ignore
        "base_urls", []
    )


logger = logging.getLogger(__name__)


def is_identifier_for_a_base_url(identifier: str, base_urls: list[str]) -> bool:
    domains = [urlparse(base_url).netloc for base_url in base_urls]

    parsed_identifier = urlparse(identifier)

    if parsed_identifier.scheme == "acct":
        identifier_domain = parsed_identifier.path.split("@")[1]
        return identifier_domain in domains
    elif parsed_identifier.scheme in ["http", "https"]:
        return parsed_identifier.netloc in domains

    return False


def is_identifier_part_of_base_urls(identifier: str, base_urls: list[str]) -> bool:
    if not identifier.startswith("acct:"):
        return False

    identifier_domain = identifier.split("@")[1]

    return any(identifier_domain == urlparse(base_url).netloc for base_url in base_urls)


async def determine_identifier_status(identifier):
    base_urls = get_base_urls()

    if is_identifier_part_of_base_urls(identifier, base_urls):
        return PublicIdentifierStatus.verified

    return PublicIdentifierStatus.unverified


def find_identifier(actor: Actor, to_find: str) -> PublicIdentifier | None:
    for identifier in actor.identifiers:
        if identifier.identifier == to_find:
            return identifier
    return None


def new_primary_preference(actor):
    preferences = [identifier.preference for identifier in actor.identifiers]
    if len(preferences) == 0:
        return 0

    return max(*preferences) + 1


async def base_urls_for_actor(session: AsyncSession, actor: Actor) -> list[str]:
    account = await account_for_actor(session, actor.actor_id)

    if account is None:
        return []

    return await allowed_base_urls(session, account)


async def handle_create_identifier(
    actor: Actor, session: AsyncSession, action: UpdateIdentifierAction
) -> None:
    base_urls = await base_urls_for_actor(session, actor)

    logger.info("Got base urls %s", ", ".join(base_urls))
    identifier = action.identifier
    if not is_identifier_for_a_base_url(identifier, base_urls):
        raise ValueError("Cannot create an identifier for this domain")

    await session.refresh(actor, attribute_names=["identifiers"])

    preference = 0

    if action.primary:
        preference = new_primary_preference(actor)

    logger.info(
        "creating identifier %s for %s",
        action.identifier,
        actor.actor_id,
    )

    session.add(
        PublicIdentifier(
            actor=actor,
            identifier=action.identifier,
            name="through_exchange",
            preference=preference,
            status=PublicIdentifierStatus.owned,
        )
    )
    await session.commit()


async def handle_add_identifier(
    actor: Actor, session: AsyncSession, action: UpdateIdentifierAction
):
    """Adds an identifier to the actor

    FIXME: Currently missing logic to verify identifier"""

    base_urls = await base_urls_for_actor(session, actor)
    identifier = action.identifier
    if is_identifier_for_a_base_url(identifier, base_urls):
        raise ValueError(
            "Cannot add an identifier for a controlled base_url use create instead"
        )
    await session.refresh(actor, attribute_names=["identifiers"])

    preference = 0

    if action.primary:
        preference = new_primary_preference(actor)

    session.add(
        PublicIdentifier(
            actor=actor,
            identifier=identifier,
            name="through_exchange",
            preference=preference,
            status=PublicIdentifierStatus.unverified,
        )
    )
    await session.commit()


async def handle_update_identifier(
    actor: Actor, session: AsyncSession, action: UpdateIdentifierAction
) -> None:
    await session.refresh(actor, attribute_names=["identifiers"])

    public_identifier = find_identifier(actor, action.identifier)
    if public_identifier is None:
        raise ValueError("Identifier not found")

    if action.primary:
        public_identifier.preference = new_primary_preference(actor)

    await session.merge(public_identifier)
