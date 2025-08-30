from pydantic import BaseModel


class ToSendMessage(BaseModel):
    """Internally used to send a message from actor
    to target with the content data"""

    actor: str
    data: dict
    target: str


class StoreActivityMessage(BaseModel):
    """Stores the activity and then sends it, an id is assigned"""

    actor: str
    data: dict
