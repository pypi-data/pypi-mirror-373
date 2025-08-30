from pydantic import BaseModel, Field


class WithActor(BaseModel):
    actor: str = Field(
        description="actor_id of the actor that received the message",
        examples=["http://host.example/actor"],
    )
