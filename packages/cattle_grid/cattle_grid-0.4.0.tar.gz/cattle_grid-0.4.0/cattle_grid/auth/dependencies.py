from typing import Annotated

from fastapi import Depends

from bovine import BovineActor as BovineActorClass
from bovine.activitystreams import Actor
from bovine.utils import parse_fediverse_handle
from bovine.crypto.signature_checker import SignatureChecker

from cattle_grid.dependencies.fastapi import Config, ClientSession
from cattle_grid.config.auth import AuthConfig as AuthConfigObject, get_auth_config
from cattle_grid.dependencies.globals import global_container

from .util import config_to_bovine_actor
from .public_key_cache import PublicKeyCache


def provide_auth_config(config: Config) -> AuthConfigObject:
    return get_auth_config(config)


AuthConfig = Annotated[AuthConfigObject, Depends(provide_auth_config)]
"""Provides the configuration for the auth module"""


def create_bovine_actor(config: AuthConfig) -> BovineActorClass:
    return config_to_bovine_actor(config)


BovineActor = Annotated[BovineActorClass, Depends(create_bovine_actor)]
"""Returns the bovine actor"""


def create_actor_object(config: AuthConfig) -> dict:
    username, _ = parse_fediverse_handle(config.actor_acct_id.removeprefix("acct:"))
    return Actor(
        id=config.actor_id,
        type="Service",
        public_key=config.public_key,
        preferred_username=username,
        public_key_name="mykey",
    ).build()


ActorObject = Annotated[dict, Depends(create_actor_object)]


async def create_signature_checker(config: AuthConfig, session: ClientSession):
    bovine_actor = config_to_bovine_actor(config)
    await bovine_actor.init(session)
    public_key_cache = PublicKeyCache(
        bovine_actor, global_container.get_session_maker()
    )
    return SignatureChecker(public_key_cache.from_cache, skip_digest_check=True)


SignatureCheckWithCache = Annotated[SignatureChecker, Depends(create_signature_checker)]
