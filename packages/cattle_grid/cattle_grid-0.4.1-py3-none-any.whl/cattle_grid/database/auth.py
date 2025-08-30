from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    """Base model"""

    pass


class RemoteIdentity(Base):
    """Stored activity in the database"""

    __tablename__ = "cattle_grid_auth_remote_identity"
    """name of the table"""

    id: Mapped[int] = mapped_column(primary_key=True)
    """The id of the key"""

    key_id: Mapped[str] = mapped_column(String(512), unique=True)
    """The URI uniquely identifying the key"""
    controller: Mapped[str] = mapped_column(String(512))
    """The URI of te controller"""
    public_key: Mapped[str] = mapped_column(String(1024))
    """The public key"""
