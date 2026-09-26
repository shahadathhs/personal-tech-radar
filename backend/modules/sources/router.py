import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models import Source
from modules.sources.schemas import SourceIn, SourceOut, SourcePatch

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
async def list_sources(db: AsyncSession = Depends(get_db)) -> list[SourceOut]:
    result = await db.execute(select(Source).order_by(Source.name))
    return [_to_out(s) for s in result.scalars()]


@router.post("")
async def create_source(payload: SourceIn, db: AsyncSession = Depends(get_db)) -> SourceOut:
    exists = await db.execute(select(Source).where(Source.name == payload.name))
    if exists.scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="Source name already exists")
    row = Source(**payload.model_dump())
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return _to_out(row)


@router.patch("/{source_id}")
async def update_source(
    source_id: uuid.UUID, payload: SourcePatch, db: AsyncSession = Depends(get_db)
) -> SourceOut:
    result = await db.execute(select(Source).where(Source.id == source_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Source not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    await db.commit()
    await db.refresh(row)
    return _to_out(row)


@router.delete("/{source_id}")
async def delete_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> dict:
    result = await db.execute(select(Source).where(Source.id == source_id))
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Source not found")
    await db.delete(row)
    await db.commit()
    return {"deleted": str(source_id)}


def _to_out(row: Source) -> SourceOut:
    return SourceOut(
        id=row.id,
        name=row.name,
        source_type=row.source_type,
        url=row.url,
        config=row.config,
        quality_weight=row.quality_weight,
        rate_limit_seconds=row.rate_limit_seconds,
        enabled=row.enabled,
        last_collected_at=row.last_collected_at,
    )
