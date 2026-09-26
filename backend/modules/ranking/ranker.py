"""Ranking — transparent weighted score (GOAL.md §23, §61, §63, §64).

Hybrid signals: AI analysis provides importance/novelty/actionability and
user_relevance; source quality and freshness are computed here. Weights are
configuration, never hardcoded magic numbers.
"""

import math
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.config import settings
from models import AIAnalysis, ContentItem, Feedback
from models.feedback import FeedbackType


@dataclass
class RankedItem:
    item: ContentItem
    analysis: AIAnalysis
    final_score: float
    freshness: float


def freshness_score(published_at: datetime | None) -> float:
    """exp(-age / decay_period) — old but major stories stay eligible."""
    if published_at is None:
        return 0.5
    age_hours = max(0.0, (datetime.now(UTC) - published_at).total_seconds() / 3600)
    return math.exp(-age_hours / settings.freshness_decay_hours)


def engagement_boost(score: int) -> float:
    """Small bounded contribution from community signal — capped at 0.05."""
    return min(0.05, score / 10000)


def final_score(
    *,
    user_relevance: float,
    importance: float,
    freshness: float,
    novelty: float,
    actionability: float,
    source_quality: float,
) -> float:
    return (
        settings.weight_relevance * user_relevance
        + settings.weight_importance * importance
        + settings.weight_freshness * freshness
        + settings.weight_novelty * novelty
        + settings.weight_actionability * actionability
        + settings.weight_source_quality * source_quality
    )


def apply_feedback_penalty(
    base: float,
    *,
    useful: int,
    not_useful: int,
    less_like: int,
) -> float:
    """Gradual learning — small nudges, never dramatic swings (GOAL.md §27)."""
    penalty = 0.02 * less_like + 0.01 * not_useful
    bonus = 0.01 * useful
    return max(0.0, min(1.0, base + bonus - penalty))


async def rank_candidates(
    db: AsyncSession, user_id: uuid.UUID, limit: int = 60
) -> list[RankedItem]:
    result = await db.execute(
        select(ContentItem, AIAnalysis)
        .join(AIAnalysis, AIAnalysis.content_item_id == ContentItem.id)
        .options(joinedload(ContentItem.source))
        .where(
            ContentItem.status == "processed",
            AIAnalysis.is_duplicate.is_(False),
        )
        .order_by(ContentItem.published_at.desc())
        .limit(limit)
    )
    rows = result.all()

    feedback_rows = await db.execute(select(Feedback).where(Feedback.user_id == user_id))
    signal: dict[uuid.UUID, dict[str, int]] = {}
    for fb in feedback_rows.scalars():
        entry = signal.setdefault(
            fb.content_item_id, {"useful": 0, "not_useful": 0, "less_like": 0}
        )
        if fb.feedback_type == FeedbackType.useful.value:
            entry["useful"] += 1
        elif fb.feedback_type == FeedbackType.not_useful.value:
            entry["not_useful"] += 1
        elif fb.feedback_type == FeedbackType.less_like.value:
            entry["less_like"] += 1

    ranked: list[RankedItem] = []
    for item, analysis in rows:
        fresh = freshness_score(item.published_at)
        quality = float(item.source.quality_weight) if item.source else 0.5
        score = final_score(
            user_relevance=analysis.user_relevance,
            importance=analysis.importance,
            freshness=fresh,
            novelty=analysis.novelty,
            actionability=analysis.actionability,
            source_quality=quality,
        )
        fb = signal.get(item.id, {"useful": 0, "not_useful": 0, "less_like": 0})
        score = apply_feedback_penalty(score, **fb)
        ranked.append(RankedItem(item=item, analysis=analysis, final_score=score, freshness=fresh))

    ranked.sort(key=lambda r: r.final_score, reverse=True)
    return ranked[:limit]


def enforce_diversity(
    ranked: list[RankedItem], max_items: int, max_per_category: int
) -> list[RankedItem]:
    """Category diversity — no single topic may dominate (GOAL.md §62)."""
    per_category: dict[str, int] = {}
    selected: list[RankedItem] = []
    overflow: list[RankedItem] = []

    for r in ranked:
        category = r.analysis.category or "Other"
        if per_category.get(category, 0) >= max_per_category:
            overflow.append(r)
            continue
        per_category[category] = per_category.get(category, 0) + 1
        selected.append(r)
        if len(selected) >= max_items:
            return selected
    return selected
