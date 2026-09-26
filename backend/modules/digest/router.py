import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models import Digest, DigestItem
from modules.ai.service import ensure_user
from modules.digest.generator import generate_digest, load_digest_items
from modules.digest.schemas import DigestItemOut, DigestListOut, DigestOut

router = APIRouter(prefix="/digests", tags=["digests"])


def _to_item_out(digest_item: DigestItem, content, analysis) -> DigestItemOut:
    return DigestItemOut(
        id=digest_item.id,
        position=digest_item.position,
        section=digest_item.section,
        category=digest_item.category,
        final_score=digest_item.final_score,
        title=content.title,
        url=content.canonical_url,
        source_name=content.source.name if content.source is not None else None,
        summary=analysis.summary,
        why_it_matters=analysis.why_it_matters,
        why_user_should_care=analysis.why_user_should_care,
        recommended_action=analysis.recommended_action,
    )


@router.get("")
async def list_digests(db: AsyncSession = Depends(get_db)) -> list[DigestListOut]:
    user = await ensure_user(db)
    item_counts = (
        select(DigestItem.digest_id, func.count().label("cnt"))
        .group_by(DigestItem.digest_id)
        .subquery()
    )
    result = await db.execute(
        select(Digest, func.coalesce(item_counts.c.cnt, 0))
        .outerjoin(item_counts, item_counts.c.digest_id == Digest.id)
        .where(Digest.user_id == user.id)
        .order_by(Digest.digest_date.desc())
    )
    return [
        DigestListOut(
            id=d.id,
            digest_date=d.digest_date,
            status=d.status,
            reading_time_minutes=d.reading_time_minutes,
            item_count=int(count),
        )
        for d, count in result.all()
    ]


@router.get("/today")
async def today_digest(db: AsyncSession = Depends(get_db)) -> DigestOut:
    user = await ensure_user(db)
    today = datetime.now(UTC).date()
    result = await db.execute(
        select(Digest).where(Digest.user_id == user.id, Digest.digest_date == today)
    )
    digest = result.scalar_one_or_none()
    if digest is None:
        raise HTTPException(status_code=404, detail="No digest generated for today yet")
    return await _digest_out(db, digest)


@router.post("/today/regenerate")
async def regenerate_today(db: AsyncSession = Depends(get_db)) -> DigestOut:
    user = await ensure_user(db)
    today = datetime.now(UTC).date()
    digest = await generate_digest(db, user.id, today)
    return await _digest_out(db, digest)


@router.get("/{digest_id}")
async def get_digest(digest_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> DigestOut:
    result = await db.execute(select(Digest).where(Digest.id == digest_id))
    digest = result.scalar_one_or_none()
    if digest is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    return await _digest_out(db, digest)


async def _digest_out(db: AsyncSession, digest: Digest) -> DigestOut:
    rows = await load_digest_items(db, digest.id)
    return DigestOut(
        id=digest.id,
        digest_date=digest.digest_date,
        status=digest.status,
        reading_time_minutes=digest.reading_time_minutes,
        generated_at=digest.generated_at,
        sent_at=digest.sent_at,
        items=[_to_item_out(d, c, a) for d, c, a in rows],
    )
