"""Objects used for the account exchange"""

from typing import List, Dict, Any
from enum import StrEnum, auto
from pydantic import BaseModel, Field, ConfigDict

from .extension import MethodInformationModel


class WithActor(BaseModel):
    """Used as base for messages requiring an actor"""

    actor: str = Field(
        examples=["http://host.example/actor/1"],
        description="""The actor performing the action""",
    )


class FetchMessage(WithActor):
    """Message to fetch an object from the Fediverse"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource to fetch""",
    )


class FetchResponse(WithActor):
    """Result of a a fetch request"""

    uri: str = Field(
        examples=["http://remote.example/object/1"],
        description="""The resource that was requested""",
    )

    data: dict | None = Field(description="""The data returned for the object""")


class TriggerMessage(WithActor):
    """Message to trigger something on the ActivityExchange"""

    model_config = ConfigDict(extra="allow")


class CreateActorRequest(BaseModel):
    """Request to create an actor"""

    base_url: str = Field(
        examples=["http://host.example"],
        serialization_alias="baseUrl",
        description="""Base url for the actor, the actor URI will be of the form `{base_url}/actor/{id}`""",
    )
    name: str | None = Field(
        default=None, examples=["alice"], description="""Internal name of the actor"""
    )

    preferred_username: str | None = Field(
        default=None,
        examples=["alice", "bob"],
        description="""
    Add a preferred username. This name will be used in acct:username@domain and supplied to webfinger. Here domain is determine from baseUrl.
    """,
        serialization_alias="preferredUsername",
    )
    profile: Dict[str, Any] = Field(
        default={},
        examples=[{"summary": "A new actor"}],
        description="""
    New profile object for the actor.
    """,
    )
    automatically_accept_followers: bool | None = Field(
        default=None,
        examples=[True, False, None],
        description="""
    Enables setting actors to automatically accept follow requests
    """,
        serialization_alias="automaticallyAcceptFollowers",
    )


class NameAndVersion(BaseModel):
    """Name and version information"""

    name: str = Field(
        examples=["cattle_grid", "CattleDrive"],
        description="""Name of the server or protocol""",
    )

    version: str = Field(
        examples=["3.1.4"],
        description="""Version of the server or protocol""",
    )


class ActorInformation(BaseModel):
    """Information about an actor"""

    id: str = Field(
        description="The URI corresponding to the actor",
        examples=["http://host.example/actor/1"],
    )
    name: str = Field(examples=["Alice"], description="Internal name of the actor")


class InformationResponse(BaseModel):
    """Response for the information request"""

    account_name: str = Field(
        examples=["alice"],
        serialization_alias="accountName",
        description="Name of the account",
    )

    actors: List[ActorInformation] = Field(
        examples=[
            [
                ActorInformation(id="http://host.example/actor/1", name="Alice"),
                ActorInformation(id="http://host.example/actor/2", name="Bob"),
            ]
        ],
        description="Actors of the account on the server",
    )

    base_urls: List[str] = Field(
        examples=[["http://host.example"]],
        serialization_alias="baseUrls",
        description="""The base urls of the server""",
    )

    backend: NameAndVersion = Field(
        examples=[NameAndVersion(name="cattle_grid", version="3.1.4")],
        description="""Name and version of the backend""",
    )

    protocol: NameAndVersion = Field(
        examples=[NameAndVersion(name="CattleDrive", version="3.1.4")],
        description="""Name and version of the protocol being used""",
    )

    method_information: List[MethodInformationModel] = Field(
        default_factory=list,
        examples=[
            [
                MethodInformationModel(
                    routing_key="send_message",
                    module="cattle_grid",
                    description="Send a message as the actor",
                )
            ]
        ],
        serialization_alias="methodInformation",
    )


class EventType(StrEnum):
    """Types of events

    ```pycon
    >>> EventType.incoming.value
    'incoming'

    ```
    """

    incoming = auto()
    outgoing = auto()
    error = auto()


class EventInformation(WithActor):
    """Send on outgoing or incoming events"""

    event_type: EventType = Field(
        examples=[EventType.incoming, EventType.outgoing],
        description="""Type of event
    
incoming means that the contained data was not generated on the actors behalf.

outgoing means that the data is being send out by the actor.""",
    )

    data: Dict[str, Any] = Field(
        examples=[
            {
                "raw": {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "type": "Create",
                    "actor": "http://host.example/actor/1",
                }
            }
        ],
        description="""The data that was exchanged. We note that this data was processed by the transformers.""",
    )


class ErrorMessage(BaseModel):
    """Message to send an exception"""

    model_config = ConfigDict(extra="allow")

    message: str = Field(description="The exception")

    routing_key: str = Field(
        examples=["send.alice.trigger.method"],
        description="""The routing key of the message that caused the error""",
    )
