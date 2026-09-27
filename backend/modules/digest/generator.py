"""Digest generation — backend selects items first, LLM only polishes (GOAL.md §28)."""

import logging
import uuid
from datetime import UTC, date, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.config import settings
from models import AIAnalysis, ContentItem, ContentStatus, Digest, DigestItem, DigestStatus
from models.digest import DigestSection
from modules.ranking.ranker import enforce_diversity, rank_candidates

logger = logging.getLogger("radar.digest.generator")

WORDS_PER_MINUTE = 200


def estimate_reading_time(texts: list[str]) -> int:
    words = sum(len(t.split()) for t in texts)
    return max(1, round(words / WORDS_PER_MINUTE))


async def generate_digest(db: AsyncSession, user_id: uuid.UUID, digest_date: date) -> Digest:
    """Build (or rebuild) the digest for one user/day. Idempotent."""
    # Remove any earlier version for this user/date so reruns are safe.
    # Bulk deletes don't fire ORM cascades and the FK isn't ON DELETE CASCADE,
    # so clear digest_items first and release their content items for re-ranking.
    existing_ids = select(Digest.id).where(
        Digest.user_id == user_id, Digest.digest_date == digest_date
    )
    item_ids = select(DigestItem.content_item_id).where(DigestItem.digest_id.in_(existing_ids))
    await db.execute(
        update(ContentItem)
        .where(ContentItem.id.in_(item_ids))
        .values(status=ContentStatus.processed.value)
    )
    await db.execute(delete(DigestItem).where(DigestItem.digest_id.in_(existing_ids)))
    await db.execute(
        delete(Digest).where(Digest.user_id == user_id, Digest.digest_date == digest_date)
    )

    ranked = await rank_candidates(db, user_id, limit=60)
    selected = enforce_diversity(
        ranked,
        max_items=settings.digest_max_items,
        max_per_category=settings.digest_max_per_category,
    )
    top = selected[: settings.digest_top_stories]

    digest = Digest(
        user_id=user_id,
        digest_date=digest_date,
        status=DigestStatus.generated.value,
        reading_time_minutes=estimate_reading_time(
            [r.analysis.summary for r in selected if r.analysis.summary]
        ),
        generated_at=datetime.now(UTC),
    )
    db.add(digest)
    await db.flush()

    for position, r in enumerate(selected):
        section = DigestSection.top_story.value if r in top else DigestSection.category.value
        db.add(
            DigestItem(
                digest_id=digest.id,
                content_item_id=r.item.id,
                position=position,
                section=section,
                category=r.analysis.category,
                final_score=r.final_score,
            )
        )
        r.item.status = ContentStatus.selected.value
        r.item.shown_count += 1
        r.item.last_shown_at = digest.generated_at

    await db.commit()
    await db.refresh(digest)
    logger.info(
        "Digest %s generated: %d items (%d top stories)", digest.id, len(selected), len(top)
    )
    return digest


async def load_digest_items(
    db: AsyncSession, digest_id: uuid.UUID
) -> list[tuple[DigestItem, ContentItem, AIAnalysis]]:
    result = await db.execute(
        select(DigestItem, ContentItem, AIAnalysis)
        .join(ContentItem, ContentItem.id == DigestItem.content_item_id)
        .join(AIAnalysis, AIAnalysis.content_item_id == ContentItem.id)
        .options(joinedload(ContentItem.source))
        .where(DigestItem.digest_id == digest_id)
        .order_by(DigestItem.position)
    )
    return [(d, c, a) for d, c, a in result.all()]
