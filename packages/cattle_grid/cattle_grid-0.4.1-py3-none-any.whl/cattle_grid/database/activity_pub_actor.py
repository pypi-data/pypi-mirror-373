from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .activity_pub import Base


class ActorStatus(StrEnum):
    """Represents the status of the actor"""

    active = auto()
    deleted = auto()


class PublicIdentifierStatus(StrEnum):
    """Represents the status of the public identifier"""

    unverified = auto()
    """This identifier could not be verified"""

    verified = auto()
    """This identifier was verified"""

    owned = auto()
    """This is an identifier owned by the cattle_grid instance"""


class Actor(Base):
    __tablename__ = "actor"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[str] = mapped_column(String(256), unique=True)
    """The id of the actor"""
    inbox_uri: Mapped[str] = mapped_column(String(256), unique=True)
    """The uri of the inbox"""
    outbox_uri: Mapped[str] = mapped_column(String(256), unique=True)
    """The uri of the outbox"""
    following_uri: Mapped[str] = mapped_column(String(256), unique=True)
    """The uri of the following collection"""
    followers_uri: Mapped[str] = mapped_column(String(256), unique=True)
    """The uri of the followers collection"""

    preferred_username: Mapped[str] = mapped_column(String(256), nullable=True)
    """The preferred username, used as the username part of the
    acct-uri of the actor, i.e. `acct:${preferred_username}@domain`.
    See [RFC 7565 The 'acct' URI Scheme](https://www.rfc-editor.org/rfc/rfc7565.html)."""

    public_key_name: Mapped[str] = mapped_column(String(256))
    """The name given to the public key, i.e. the id will be
    `${actor_id}#${public_key_name}."""
    public_key: Mapped[str] = mapped_column(Text())
    """The public key"""

    automatically_accept_followers: Mapped[bool] = mapped_column(Boolean())
    """Set to true to indicate cattle_grid should automatically
    accept follow requests"""
    profile: Mapped[dict] = mapped_column(JSON())
    """Additional profile values"""

    status: Mapped[ActorStatus] = mapped_column(String(7))
    """Represents the status of the actor"""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    identifiers: Mapped[list["PublicIdentifier"]] = relationship(viewonly=True)
    followers: Mapped[list["Follower"]] = relationship(viewonly=True)
    following: Mapped[list["Following"]] = relationship(viewonly=True)
    blocking: Mapped[list["Blocking"]] = relationship(viewonly=True)


class Follower(Base):
    """The people that follow the actor"""

    __tablename__ = "follower"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actor.id", ondelete="CASCADE"))
    actor: Mapped[Actor] = relationship()

    follower: Mapped[str] = mapped_column(String(256))
    request: Mapped[str] = mapped_column(String(256))
    accepted: Mapped[bool] = mapped_column(Boolean())


class Following(Base):
    """The people the actor is following"""

    __tablename__ = "following"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actor.id", ondelete="CASCADE"))
    actor: Mapped[Actor] = relationship()

    following: Mapped[str] = mapped_column(String(256))
    request: Mapped[str] = mapped_column(String(256))
    accepted: Mapped[bool] = mapped_column(Boolean())


class Blocking(Base):
    """The people the actor is blocking"""

    __tablename__ = "blocking"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actor.id", ondelete="CASCADE"))
    actor: Mapped[Actor] = relationship()

    blocking: Mapped[str] = mapped_column(String(256))
    request: Mapped[str] = mapped_column(String(256))
    active: Mapped[bool] = mapped_column(Boolean())


class StoredActivity(Base):
    """cattle_grid generates activities under some
    circumstances (see FIXME). These will be stored
    in this table"""

    __tablename__ = "storedactivity"
    id: Mapped[str] = mapped_column(String(256), primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actor.id", ondelete="CASCADE"))
    actor: Mapped[Actor] = relationship(lazy="joined")

    data: Mapped[dict] = mapped_column(JSON())
    published: Mapped[datetime] = mapped_column()


class PublicIdentifier(Base):
    """Public identifier"""

    __tablename__ = "publicidentifier"
    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("actor.id", ondelete="CASCADE"))
    actor: Mapped[Actor] = relationship(lazy="joined")

    name: Mapped[str] = mapped_column(String(256))
    identifier: Mapped[str] = mapped_column(String(256), unique=True)
    preference: Mapped[int] = mapped_column(default=0)
    status: Mapped[PublicIdentifierStatus] = mapped_column(
        String(10), default=PublicIdentifierStatus.verified
    )
