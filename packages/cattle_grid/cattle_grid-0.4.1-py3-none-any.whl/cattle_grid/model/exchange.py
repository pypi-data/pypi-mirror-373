from enum import StrEnum, auto
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Dict, Any, List

from .common import WithActor


class UpdateActionType(StrEnum):
    """Available actions for updating the actor"""

    add_identifier = auto()
    """Adds a new identifier. The identifier is assumed to already exist."""
    create_identifier = auto()
    """Creates a new identifier. Must be on a domain controlled by cattle_grid and enabled in the account"""
    update_identifier = auto()
    """Updates an identifer"""
    remove_identifier = auto()
    """Removes an identifier"""

    rename = auto()
    """Updates the internal name of the actor"""

    update_property_value = auto()
    """Adds or updates a property value of the actor"""
    remove_property_value = auto()
    """Removes a property value"""


class UpdateAction(BaseModel):
    """Action to update an actor"""

    model_config = ConfigDict(
        extra="allow",
    )

    action: UpdateActionType


class UpdateIdentifierAction(UpdateAction):
    """Used to update an identifier of the actor"""

    identifier: str = Field(
        description="The identifier", examples=["acct:alice@domain.example"]
    )
    primary: bool = Field(
        False,
        description="Set the identifier as the primary one, if the identifier corresponds to an acct-uri this will update the primary identifier",
    )


class RenameActorAction(UpdateAction):
    """Update the internal name of the actor"""

    name: str = Field(description="The new name of the actor")


class UpdatePropertyValueAction(UpdateAction):
    """Update a property value of the actor"""

    key: str = Field(
        examples=["author"],
        description="The key of the property value to be created, updated, or deleted",
    )
    value: str | None = Field(
        None,
        examples=["Alice"],
        description="The value of the property value",
    )


class UpdateActorMessage(WithActor):
    """
    Allows one to update the actor object
    """

    # model_config = ConfigDict(
    #     extra="forbid",
    # )

    profile: Dict[str, Any] | None = Field(
        default=None,
        examples=[{"summary": "A new description of the actor"}],
        description="""
    New profile object for the actor. The fields.
    """,
    )
    autoFollow: bool | None = Field(
        default=None,
        examples=[True, False, None],
        description="""
    Enables setting actors to automatically accept follow requests
    """,
    )

    actions: List[UpdateAction] = Field(
        default_factory=list,
        description="""Actions to be taken when updating the profile""",
    )

    @field_serializer("actions")
    def serialize_dt(self, actions: List[UpdateAction], _info):
        return [action.model_dump() for action in actions]


class DeleteActorMessage(WithActor):
    """
    Allows one to delete the actor object
    """

    model_config = ConfigDict(
        extra="forbid",
    )
