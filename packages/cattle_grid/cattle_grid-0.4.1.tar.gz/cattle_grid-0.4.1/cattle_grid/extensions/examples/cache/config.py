from pydantic import BaseModel, Field


class CacheConfiguration(BaseModel):
    connection_url: str = Field(default="redis://localhost:6379")
    """Connection url to the key value instance, e.g. redis"""

    duration: int = Field(default=3600)
    """Duration to cache in second"""
