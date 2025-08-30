from pydantic import BaseModel, Field, ConfigDict


class SignInData(BaseModel):
    """Used to sign into an account"""

    name: str = Field(description="Name of the account")
    password: str = Field(description="Password")


class TokenResponse(BaseModel):
    """Returns the token to be used with Bearer authentication, i.e.
    add the Header `Authorization: Bearer {token}` to the request"""

    token: str = Field(description="The token")


class LookupRequest(BaseModel):
    actor_id: str = Field(alias="actorId")
    uri: str


class LookupResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    raw: dict


class PerformRequest(BaseModel):
    """Request send to enqueue an action"""

    model_config = ConfigDict(extra="allow")

    actor: str = Field(examples=["http://actor.example/someId"])
    """The actor id, must be long to the account"""


class CreateActorRequest(BaseModel):
    """Used to create an actor for the account"""

    base_url: str = Field(
        alias="baseUrl",
        examples=["http://domain.example"],
        description="""Base url of the actor. The actor URI will be
    of the form `{baseUrl}/actor/some_secret`
    """,
    )

    handle: str | None = Field(
        None,
        examples=["alice"],
        description="""If present, an acct-uri of the form `acct:{handle}@{domain}` where domain is determined from `baseUrl` is created""",
    )

    name: str | None = Field(
        None,
        examples=["Alice"],
        description="""Internal name of the actor. Used to simplify display of the actor.""",
    )
