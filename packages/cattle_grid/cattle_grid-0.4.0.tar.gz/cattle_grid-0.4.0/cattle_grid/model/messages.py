from typing import Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CreateActorMessage(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )
    baseUrl: str = Field(
        examples=["http://local.example/"],
        description="""
    base url used to create the user on. Can contain a path
    """,
    )
    preferredUsername: str | None = Field(
        None,
        examples=["alice", "bob"],
        description="""
    Add a preferred username. This name will be used in acct:username@domain and supplied to webfinger. Here domain is determine from baseUrl.
    """,
    )
    profile: Dict[str, Any] = Field(
        {},
        examples=[{"summary": "A new actor"}],
        description="""
    New profile object for the actor. The fields.
    """,
    )
    autoFollow: bool = Field(
        False,
        examples=[True],
        description="""
    Enables setting actors to automatically accept follow requests
    """,
    )
