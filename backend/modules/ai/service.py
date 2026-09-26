"""Analyze pending content items with the configured AI provider."""

import logging
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models import AIAnalysis, ContentItem, ContentStatus, Interest, User
from modules.ai.schemas import ContentAnalysis
from modules.ai.zai import get_provider

logger = logging.getLogger("radar.ai.service")


def build_user_context(interests: list[str], role: str, excluded: list[str]) -> str:
    parts = [f"Role: {role}"]
    if interests:
        parts.append(f"Interests: {', '.join(interests)}")
    if excluded:
        parts.append(f"Explicitly NOT interested in: {', '.join(excluded)}")
    return "\n".join(parts)


async def load_user_context(db: AsyncSession, user_id: uuid.UUID) -> str:
    result = await db.execute(select(Interest.name).where(Interest.user_id == user_id))
    interests = list(result.scalars().all())
    role = "software engineer"
    excluded: list[str] = []
    return build_user_context(interests, role, excluded)


async def analyze_pending(db: AsyncSession, user_id: uuid.UUID, limit: int = 100) -> int:
    """Analyze discovered items that have no analysis yet. Returns count."""
    provider = get_provider()
    if not settings.ai_api_key:
        logger.warning("AI_API_KEY not configured — skipping analysis")
        return 0

    user_context = await load_user_context(db, user_id)
    result = await db.execute(
        select(ContentItem)
        .where(
            ContentItem.status == ContentStatus.discovered.value,
            ContentItem.source_id.isnot(None),
            ~ContentItem.id.in_(select(AIAnalysis.content_item_id)),
        )
        .order_by(ContentItem.discovered_at.desc())
        .limit(limit)
    )
    items = list(result.scalars().all())
    analyzed = 0

    for item in items:
        try:
            analysis: ContentAnalysis = await provider.analyze(
                title=item.title,
                description=item.description,
                content=item.content,
                user_context=user_context,
            )
        except Exception:
            logger.exception("AI analysis failed for item %s — skipping", item.id)
            continue

        if analysis.is_duplicate:
            item.status = ContentStatus.rejected.value
        else:
            item.status = ContentStatus.processed.value
        db.add(
            AIAnalysis(
                content_item_id=item.id,
                summary=analysis.summary,
                category=analysis.category,
                subcategory=analysis.subcategory,
                topics=analysis.topics,
                importance=analysis.importance,
                user_relevance=analysis.user_relevance,
                novelty=analysis.novelty,
                actionability=analysis.actionability,
                credibility=analysis.credibility,
                is_breaking=analysis.is_breaking,
                is_duplicate=analysis.is_duplicate,
                why_it_matters=analysis.why_it_matters,
                why_user_should_care=analysis.why_user_should_care,
                recommended_action=analysis.recommended_action,
                model=provider.model,
            )
        )
        analyzed += 1

    await db.commit()
    logger.info("Analyzed %d/%d pending items", analyzed, len(items))
    return analyzed


async def ensure_user(db: AsyncSession) -> User:
    """Single-user MVP: get or create the first user (GOAL.md §14)."""
    result = await db.execute(select(User).limit(1))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(email="owner@localhost", timezone=settings.timezone)
        db.add(user)
        await db.flush()
    return user
