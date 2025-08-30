from typing import List
from urllib.parse import urlparse

from sqlalchemy import func, select

from cattle_grid.database.activity_pub_actor import (
    Actor,
    PublicIdentifierStatus,
    PublicIdentifier,
)


def determine_preferred_username(identifiers: List[str], actor_id: str) -> str | None:
    """Determine the preferred username from the sorted identifiers.
    The result is the name of the first acct-uri whose domain matches
    the actor id.

    ```pycon
    >>> determine_preferred_username(["acct:alice@other.example",
    ...     "acct:alice@actor.example"], "http://actor.example/actor")
    'alice'

    ```
    """
    actor_domain = urlparse(actor_id).netloc
    for identifier in identifiers:
        if identifier.startswith("acct:"):
            handle, domain = identifier.removeprefix("acct:").split("@")
            if domain == actor_domain:
                return handle

    return None


def collect_identifiers_for_actor(actor: Actor) -> list[str]:
    try:
        filtered_identifiers = [
            (identifier.identifier, identifier.preference)
            for identifier in actor.identifiers
            if identifier.status
            in [PublicIdentifierStatus.verified, PublicIdentifierStatus.owned]
        ]
        return [
            x[0] for x in sorted(filtered_identifiers, key=lambda x: x[1], reverse=True)
        ]
    except Exception:
        return []


async def identifier_in_list_exists(session, identifiers: list[str]) -> bool:
    result = await session.scalar(
        select(func.count()).where(PublicIdentifier.identifier.in_(identifiers))
    )

    return result > 0
