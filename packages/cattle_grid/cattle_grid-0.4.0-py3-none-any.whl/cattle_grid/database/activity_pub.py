from sqlalchemy import String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""

    pass


class Credential(Base):
    """Stored credential"""

    __tablename__ = "credential"
    """name of the table"""

    id: Mapped[int] = mapped_column(primary_key=True)
    """primary key"""

    actor_id: Mapped[str] = mapped_column(String(256))
    """The id of the actor the key belongs to"""
    identifier: Mapped[str] = mapped_column(String(256), unique=True)
    """The identifier of the key"""

    secret: Mapped[str] = mapped_column(Text())
    """The secret underlying the private key"""


class InboxLocation(Base):
    """Describes the location of an inbox. Used to send
    ActivityPub Activities addressed to the actor to the
    corresponding inbox.

    This information is also collected for remote actors.
    """

    __tablename__ = "inboxlocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(256), unique=True)
    inbox: Mapped[str] = mapped_column(String(256))
