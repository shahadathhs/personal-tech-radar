"""Deduplication — deterministic first, never LLM-dependent (GOAL.md §22, §35)."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ContentItem, SourceOccurrence

logger = logging.getLogger("radar.ingestion.dedup")


async def find_canonical(
    db: AsyncSession, *, content_hash: str, external_id: str, source_id
) -> ContentItem | None:
    """Return an existing item this raw input duplicates, if any.

    Match order: exact (source_id, external_id), then content hash.
    """
    result = await db.execute(
        select(ContentItem).where(
            ContentItem.source_id == source_id, ContentItem.external_id == external_id
        )
    )
    item = result.scalar_one_or_none()
    if item is not None:
        return item

    result = await db.execute(
        select(ContentItem).where(ContentItem.content_hash == content_hash).limit(1)
    )
    return result.scalar_one_or_none()


async def record_occurrence(db: AsyncSession, item: ContentItem, *, source_id, url: str) -> None:
    exists = await db.execute(
        select(SourceOccurrence.id).where(
            SourceOccurrence.content_item_id == item.id,
            SourceOccurrence.source_id == source_id,
        )
    )
    if exists.scalar_one_or_none() is None:
        db.add(SourceOccurrence(content_item_id=item.id, source_id=source_id, external_url=url))


def dedupe_batch(items: list) -> list:
    """Within-batch dedup by content hash (first occurrence wins)."""
    seen: set[str] = set()
    unique = []
    for raw in items:
        from modules.ingestion.normalizer import canonicalize_url, content_hash

        chash = content_hash(raw.title, canonicalize_url(raw.url))
        if chash in seen:
            logger.debug("Dropping in-batch duplicate: %s", raw.title)
            continue
        seen.add(chash)
        unique.append(raw)
    return unique
