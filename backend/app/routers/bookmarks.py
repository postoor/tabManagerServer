import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from typing import List

from app.database import get_db
from app.models import User, Collection, Bookmark
from app.schemas import (
    CollectionCreate, CollectionUpdate, CollectionResponse,
    BookmarkCreate, BookmarkUpdate, BookmarkResponse,
    ReorderRequest,
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


# ─── Collections ─────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CollectionResponse])
async def get_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id)
        .options(selectinload(Collection.bookmarks))
        .order_by(Collection.position, Collection.created_at)
    )
    collections = result.scalars().all()
    return collections


@router.post("/collections", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    data: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Find max position
    result = await db.execute(
        select(Collection).where(Collection.user_id == current_user.id)
    )
    existing = result.scalars().all()
    max_position = max((c.position for c in existing), default=-1) + 1

    collection = Collection(
        user_id=current_user.id,
        title=data.title,
        labels=json.dumps(data.labels),
        position=data.position if data.position else max_position,
    )
    db.add(collection)
    await db.flush()
    await db.refresh(collection, ["bookmarks"])
    return collection


@router.put("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: str,
    data: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Collection)
        .where(Collection.id == collection_id, Collection.user_id == current_user.id)
        .options(selectinload(Collection.bookmarks))
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    if data.title is not None:
        collection.title = data.title
    if data.labels is not None:
        collection.labels = json.dumps(data.labels)
    if data.position is not None:
        collection.position = data.position

    await db.flush()
    await db.refresh(collection)
    return collection


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    await db.delete(collection)
    await db.flush()


# ─── Bookmarks ────────────────────────────────────────────────────────────────

@router.post("/collections/{collection_id}/bookmarks", response_model=BookmarkResponse, status_code=status.HTTP_201_CREATED)
async def add_bookmark(
    collection_id: str,
    data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Collection).where(
            Collection.id == collection_id,
            Collection.user_id == current_user.id,
        )
    )
    collection = result.scalar_one_or_none()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    # Find max position within this collection
    bk_result = await db.execute(
        select(Bookmark).where(Bookmark.collection_id == collection_id)
    )
    existing_bks = bk_result.scalars().all()
    max_pos = max((b.position for b in existing_bks), default=-1) + 1

    bookmark = Bookmark(
        collection_id=collection_id,
        title=data.title,
        url=data.url,
        custom_title=data.custom_title,
        custom_description=data.custom_description,
        favicon_url=data.favicon_url,
        position=data.position if data.position else max_pos,
    )
    db.add(bookmark)
    await db.flush()
    await db.refresh(bookmark)
    return bookmark


@router.put("/bookmarks/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: str,
    data: BookmarkUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark)
        .join(Collection)
        .where(Bookmark.id == bookmark_id, Collection.user_id == current_user.id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    if data.title is not None:
        bookmark.title = data.title
    if data.url is not None:
        bookmark.url = data.url
    if data.custom_title is not None:
        bookmark.custom_title = data.custom_title
    if data.custom_description is not None:
        bookmark.custom_description = data.custom_description
    if data.favicon_url is not None:
        bookmark.favicon_url = data.favicon_url
    if data.position is not None:
        bookmark.position = data.position

    await db.flush()
    await db.refresh(bookmark)
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark)
        .join(Collection)
        .where(Bookmark.id == bookmark_id, Collection.user_id == current_user.id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    await db.delete(bookmark)
    await db.flush()


@router.post("/reorder", status_code=status.HTTP_200_OK)
async def reorder(
    data: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if data.type == "collection":
        for item in data.items:
            result = await db.execute(
                select(Collection).where(
                    Collection.id == item.id,
                    Collection.user_id == current_user.id,
                )
            )
            collection = result.scalar_one_or_none()
            if collection:
                collection.position = item.position
    elif data.type == "bookmark":
        for item in data.items:
            result = await db.execute(
                select(Bookmark)
                .join(Collection)
                .where(Bookmark.id == item.id, Collection.user_id == current_user.id)
            )
            bookmark = result.scalar_one_or_none()
            if bookmark:
                bookmark.position = item.position
    else:
        raise HTTPException(status_code=400, detail="Invalid reorder type")

    await db.flush()
    return {"status": "ok"}
