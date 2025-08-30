from enum import StrEnum, auto
from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


from .activity_pub import Base


class ActorStatus(StrEnum):
    """Status actors can have for an account"""

    active = auto()
    deleted = auto()


class Account(Base):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    password_hash: Mapped[str] = mapped_column(String(256))
    meta_information: Mapped[dict] = mapped_column(JSON(), default={})

    actors: Mapped[list["ActorForAccount"]] = relationship(viewonly=True)
    permissions: Mapped[list["Permission"]] = relationship(viewonly=True)


class ActorForAccount(Base):
    __tablename__ = "actorforaccount"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE")
    )
    account: Mapped[Account] = relationship(lazy="joined")

    actor: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(
        String(256),
        default="NO NAME",
    )
    status: Mapped[ActorStatus] = mapped_column(String(10), default=ActorStatus.active)

    groups: Mapped[list["ActorGroup"]] = relationship(viewonly=True)


class AuthenticationToken(Base):
    __tablename__ = "authenticationtoken"
    token: Mapped[str] = mapped_column(String(65), primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE")
    )
    account: Mapped[Account] = relationship(lazy="joined")


class Permission(Base):
    __tablename__ = "permission"
    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="CASCADE")
    )
    account: Mapped[Account] = relationship(lazy="joined")

    name: Mapped[str] = mapped_column(String(256))


class ActorGroup(Base):
    __tablename__ = "actorgroup"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("actorforaccount.id", ondelete="CASCADE")
    )
    actor: Mapped[ActorForAccount] = relationship(lazy="joined")
