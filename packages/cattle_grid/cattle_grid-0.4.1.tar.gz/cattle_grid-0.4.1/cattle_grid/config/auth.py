import logging
import secrets
import tomli_w
from typing import Set
from urllib.parse import urlparse

from dynaconf import Dynaconf
from pydantic import BaseModel, ValidationError, field_serializer
from functools import lru_cache

from bovine.crypto import generate_rsa_public_private_key

from .settings import get_settings

logger = logging.getLogger(__name__)


class AuthNotConfigured(Exception): ...


class AuthConfig(BaseModel):
    """Configures the Authorization layer"""

    actor_id: str
    """actor_id for the Application actor used to fetch public keys"""
    actor_acct_id: str
    """acct uri of the Application Actor used to fetch public keys"""
    public_key: str
    """Public key of the Application actor"""
    private_key: str
    """Private key of the Application actor"""

    domain_blocks: Set[str]
    """Set of blocked domains"""

    require_signature_for_activity_pub: bool = True
    """If set to true, all requests with accept type that match activitypub must be signed"""

    @field_serializer("domain_blocks")
    def serialize_domain_blocks(self, domain_blocks: Set[str], _info):
        return list(domain_blocks)


@lru_cache
def get_auth_config(settings: Dynaconf = get_settings()) -> AuthConfig:
    """Returns the configuration for authorization

    :returns:
    """
    try:
        auth = settings.get("auth")  # type:ignore
        if not auth:
            raise AuthNotConfigured("No authorization configuration found")

        data = {
            "actor_id": auth.actor_id,
            "actor_acct_id": auth.actor_acct_id,
            "public_key": auth.public_key,
            "private_key": auth.private_key,
            "domain_blocks": auth.get("domain_blocks", []),
            "require_signature_for_activity_pub": auth.get(
                "require_signature_for_activity_pub", True
            ),
        }
        return AuthConfig.model_validate(data)

    except ValidationError:
        raise AuthNotConfigured(
            "Authorization not configured or configured incorrectly"
        )


def new_auth_config(actor_id: str, username: str | None = None) -> AuthConfig:
    """Creates a new authorization configuration"""
    if not username:
        username = secrets.token_urlsafe(12)

    domain = urlparse(actor_id).netloc
    acct_uri = f"acct:{username}@{domain}"

    public_key, private_key = generate_rsa_public_private_key()

    auth_config = AuthConfig(
        actor_id=actor_id,
        actor_acct_id=acct_uri,
        public_key=public_key,
        private_key=private_key,
        domain_blocks=set(),
    )

    return auth_config


def save_auth_config(filename: str, config: AuthConfig) -> None:
    """Saves the authorization configuration to a file"""
    with open(filename, "wb") as fp:
        tomli_w.dump({"auth": config.model_dump()}, fp, multiline_strings=True)
