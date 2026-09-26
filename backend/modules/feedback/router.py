from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models import ContentItem, Feedback
from models.feedback import FeedbackType
from modules.ai.service import ensure_user
from modules.feedback.schemas import FeedbackIn, FeedbackOut, SavedItemOut

router = APIRouter(tags=["feedback"])


@router.post("/feedback")
async def submit_feedback(payload: FeedbackIn, db: AsyncSession = Depends(get_db)) -> FeedbackOut:
    user = await ensure_user(db)
    feedback = Feedback(
        user_id=user.id,
        content_item_id=payload.content_item_id,
        feedback_type=payload.feedback_type.value,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return FeedbackOut(
        id=feedback.id,
        content_item_id=feedback.content_item_id,
        feedback_type=feedback.feedback_type,
        created_at=feedback.created_at,
    )


@router.get("/feedback/saved")
async def saved_items(db: AsyncSession = Depends(get_db)) -> list[SavedItemOut]:
    """Saved items remain accessible through the API (GOAL.md §48)."""
    user = await ensure_user(db)
    result = await db.execute(
        select(Feedback, ContentItem)
        .join(ContentItem, ContentItem.id == Feedback.content_item_id)
        .where(Feedback.user_id == user.id, Feedback.feedback_type == FeedbackType.save.value)
        .order_by(Feedback.created_at.desc())
    )
    return [
        SavedItemOut(
            content_item_id=item.id,
            title=item.title,
            url=item.canonical_url,
            source_name=item.source.name if item.source is not None else None,
            saved_at=fb.created_at,
        )
        for fb, item in result.all()
    ]
