from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, field_validator
import uuid


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


# ─── Bookmarks ────────────────────────────────────────────────────────────────

class BookmarkCreate(BaseModel):
    title: str = ""
    url: str
    custom_title: str = ""
    custom_description: str = ""
    favicon_url: Optional[str] = None
    position: int = 0


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    custom_title: Optional[str] = None
    custom_description: Optional[str] = None
    favicon_url: Optional[str] = None
    position: Optional[int] = None


class BookmarkResponse(BaseModel):
    id: str
    collection_id: str
    title: str
    url: str
    custom_title: str
    custom_description: str
    favicon_url: Optional[str]
    position: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ─── Collections ─────────────────────────────────────────────────────────────

class CollectionCreate(BaseModel):
    title: str = "New Collection"
    labels: List[Any] = []
    position: int = 0


class CollectionUpdate(BaseModel):
    title: Optional[str] = None
    labels: Optional[List[Any]] = None
    position: Optional[int] = None


class CollectionResponse(BaseModel):
    id: str
    user_id: str
    title: str
    labels: List[Any]
    position: int
    bookmarks: List[BookmarkResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("labels", mode="before")
    @classmethod
    def parse_labels(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []


# ─── Reorder ──────────────────────────────────────────────────────────────────

class ReorderItem(BaseModel):
    id: str
    position: int


class ReorderRequest(BaseModel):
    type: str  # "collection" or "bookmark"
    items: List[ReorderItem]


# ─── Sync (Toby-compatible format v3) ────────────────────────────────────────

class TobyCard(BaseModel):
    id: str
    title: str
    url: str
    customTitle: str = ""
    customDescription: str = ""


class TobyList(BaseModel):
    id: str
    title: str
    labels: List[Any] = []
    cards: List[TobyCard] = []


class SyncPushRequest(BaseModel):
    version: int = 3
    lists: List[TobyList]


class SyncPullResponse(BaseModel):
    version: int = 3
    lists: List[TobyList]


# ─── Sync Status ──────────────────────────────────────────────────────────────

class SyncStatusResponse(BaseModel):
    last_push: Optional[datetime]
    last_pull: Optional[datetime]
    collection_count: int
    bookmark_count: int
