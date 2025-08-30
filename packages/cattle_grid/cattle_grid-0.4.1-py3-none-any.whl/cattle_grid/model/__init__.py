from typing import Any, Dict

from pydantic import BaseModel, ConfigDict, Field

from .common import WithActor


class ActivityMessage(WithActor):
    """
    Message that contains an Activity. Activity is used as the name for the 'data object' being exchanged, as is common in the Fediverse
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    data: Dict[str, Any] = Field(description="The activity")


class SharedInboxMessage(BaseModel):
    """
    Message that contains an Activity. In difference to the ActivityMessage this message does not have an actor, and thus its recipients will be determined by cattle_grid.
    """

    model_config = ConfigDict(
        extra="forbid",
    )
    data: Dict[str, Any] = Field(description="Activity")


class FetchMessage(WithActor):
    """
    Used to request an ActivityPub object to be retrieved
    """

    model_config = ConfigDict(
        extra="forbid",
    )

    uri: str = Field(description="URI of the object being retrieved")
