import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, ForeignKey, Text
)
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="user", cascade="all, delete-orphan")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False, default="New Collection")
    labels = Column(Text, nullable=False, default="[]")  # JSON stored as text
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    user = relationship("User", back_populates="collections")
    bookmarks = relationship(
        "Bookmark",
        back_populates="collection",
        cascade="all, delete-orphan",
        order_by="Bookmark.position",
    )


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    collection_id = Column(String(36), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False, default="")
    url = Column(Text, nullable=False)
    custom_title = Column(String(500), nullable=False, default="")
    custom_description = Column(Text, nullable=False, default="")
    favicon_url = Column(Text, nullable=True)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    collection = relationship("Collection", back_populates="bookmarks")


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(String(255), nullable=True)
    action = Column(String(50), nullable=False)  # push / pull
    synced_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="sync_logs")
