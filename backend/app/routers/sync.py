import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, Collection, Bookmark, SyncLog
from app.schemas import (
    SyncPushRequest, SyncPullResponse,
    TobyList, TobyCard, SyncStatusResponse,
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/push", response_model=SyncPullResponse)
async def sync_push(
    data: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_device_id: Optional[str] = Header(None),
):
    """
    Accept Toby-format data and upsert all collections and bookmarks.
    This is a full-replace strategy: incoming data is authoritative.
    """
    incoming_collection_ids = {lst.id for lst in data.lists}

    # Fetch existing collections for this user
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == current_user.id)
        .options(selectinload(Collection.bookmarks))
    )
    existing_collections = {c.id: c for c in result.scalars().all()}

    # Delete collections not present in incoming data
    for col_id, col in list(existing_collections.items()):
        if col_id not in incoming_collection_ids:
            await db.delete(col)

    # Upsert collections and bookmarks
    for position, toby_list in enumerate(data.lists):
        is_new = toby_list.id not in existing_collections

        if not is_new:
            collection = existing_collections[toby_list.id]
            collection.title = toby_list.title
            collection.labels = json.dumps(toby_list.labels)
            collection.position = position
            # bookmarks already eagerly loaded via selectinload above
            existing_bookmarks = {b.id: b for b in collection.bookmarks}
        else:
            collection = Collection(
                id=toby_list.id,
                user_id=current_user.id,
                title=toby_list.title,
                labels=json.dumps(toby_list.labels),
                position=position,
            )
            db.add(collection)
            await db.flush()
            existing_collections[toby_list.id] = collection
            # New collection — no bookmarks exist yet, skip relationship access
            # to avoid triggering an async lazy load in a sync context.
            existing_bookmarks = {}

        incoming_card_ids = {card.id for card in toby_list.cards}

        # Delete bookmarks not present
        for bk_id, bk in list(existing_bookmarks.items()):
            if bk_id not in incoming_card_ids:
                await db.delete(bk)

        # Upsert bookmarks
        for card_pos, card in enumerate(toby_list.cards):
            if card.id in existing_bookmarks:
                bk = existing_bookmarks[card.id]
                bk.title = card.title
                bk.url = card.url
                bk.custom_title = card.customTitle
                bk.custom_description = card.customDescription
                bk.position = card_pos
            else:
                bk = Bookmark(
                    id=card.id,
                    collection_id=toby_list.id,
                    title=card.title,
                    url=card.url,
                    custom_title=card.customTitle,
                    custom_description=card.customDescription,
                    position=card_pos,
                )
                db.add(bk)

    await db.flush()

    # Log sync
    log = SyncLog(
        user_id=current_user.id,
        device_id=x_device_id,
        action="push",
    )
    db.add(log)
    await db.flush()

    # Return current state
    return await _build_pull_response(current_user.id, db)


@router.get("/pull", response_model=SyncPullResponse)
async def sync_pull(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_device_id: Optional[str] = Header(None),
):
    """Return all user data in Toby-compatible format."""
    log = SyncLog(
        user_id=current_user.id,
        device_id=x_device_id,
        action="pull",
    )
    db.add(log)
    await db.flush()

    return await _build_pull_response(current_user.id, db)


@router.get("/status", response_model=SyncStatusResponse)
async def sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Last push
    push_result = await db.execute(
        select(SyncLog)
        .where(SyncLog.user_id == current_user.id, SyncLog.action == "push")
        .order_by(SyncLog.synced_at.desc())
        .limit(1)
    )
    last_push_log = push_result.scalar_one_or_none()

    # Last pull
    pull_result = await db.execute(
        select(SyncLog)
        .where(SyncLog.user_id == current_user.id, SyncLog.action == "pull")
        .order_by(SyncLog.synced_at.desc())
        .limit(1)
    )
    last_pull_log = pull_result.scalar_one_or_none()

    # Collection count
    col_count_result = await db.execute(
        select(func.count()).where(Collection.user_id == current_user.id)
    )
    col_count = col_count_result.scalar()

    # Bookmark count
    bk_count_result = await db.execute(
        select(func.count(Bookmark.id))
        .join(Collection)
        .where(Collection.user_id == current_user.id)
    )
    bk_count = bk_count_result.scalar()

    return SyncStatusResponse(
        last_push=last_push_log.synced_at if last_push_log else None,
        last_pull=last_pull_log.synced_at if last_pull_log else None,
        collection_count=col_count or 0,
        bookmark_count=bk_count or 0,
    )


async def _build_pull_response(user_id: str, db: AsyncSession) -> SyncPullResponse:
    result = await db.execute(
        select(Collection)
        .where(Collection.user_id == user_id)
        .options(selectinload(Collection.bookmarks))
        .order_by(Collection.position, Collection.created_at)
    )
    collections = result.scalars().all()

    toby_lists = []
    for col in collections:
        cards = []
        for bk in sorted(col.bookmarks, key=lambda b: b.position):
            cards.append(
                TobyCard(
                    id=bk.id,
                    title=bk.title,
                    url=bk.url,
                    customTitle=bk.custom_title,
                    customDescription=bk.custom_description,
                )
            )
        labels = json.loads(col.labels) if isinstance(col.labels, str) else (col.labels or [])
        toby_lists.append(
            TobyList(
                id=col.id,
                title=col.title,
                labels=labels,
                cards=cards,
            )
        )

    return SyncPullResponse(version=3, lists=toby_lists)
