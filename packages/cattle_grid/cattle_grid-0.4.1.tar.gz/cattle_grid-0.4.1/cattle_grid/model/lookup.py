from typing import Callable, Awaitable

from pydantic import BaseModel, Field


class Lookup(BaseModel):
    """
    Lookup of something from the Fediverse
    """

    uri: str = Field(
        examples=["http://actor.example", "acct:user@actor.example"],
        description="""The uri being looked up""",
    )

    actor: str = Field(
        examples=["http://abel.example/actor"],
        description="""The actor performing the lookup""",
    )

    result: dict | None = Field(
        default=None,
        examples=[{"id": "http://actor.example", "type": "Person", "name": "Jane Doe"}],
        description="""The result of the lookup, None if no result yet,
    the result will be returned once the lookup is finished""",
    )


LookupMethod = Callable[[Lookup], Awaitable[Lookup]]
"""Alias for the Lookup Method"""
