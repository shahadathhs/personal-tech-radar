from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models import AIAnalysis, ContentItem
from modules.content.schemas import ContentItemOut, ContentListOut

router = APIRouter(prefix="/content", tags=["content"])


@router.get("")
async def list_content(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ContentListOut:
    base = select(ContentItem, AIAnalysis).outerjoin(
        AIAnalysis, AIAnalysis.content_item_id == ContentItem.id
    )
    count_query = select(func.count()).select_from(ContentItem)
    if status:
        base = base.where(ContentItem.status == status)
        count_query = count_query.where(ContentItem.status == status)

    total = await db.scalar(count_query)
    result = await db.execute(
        base.order_by(ContentItem.discovered_at.desc()).offset(offset).limit(limit)
    )
    items = [
        ContentItemOut(
            id=item.id,
            title=item.title,
            url=item.canonical_url,
            source_name=item.source.name if item.source is not None else None,
            status=item.status,
            category=analysis.category if analysis else None,
            summary=analysis.summary if analysis else None,
            published_at=item.published_at,
            discovered_at=item.discovered_at,
        )
        for item, analysis in result.all()
    ]
    return ContentListOut(items=items, total=int(total or 0))
