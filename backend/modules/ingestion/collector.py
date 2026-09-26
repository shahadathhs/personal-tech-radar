"""Collector — fetch from all enabled sources and persist new items.

Idempotent: rerunning never duplicates content (GOAL.md §37). A failing
source is logged and skipped (GOAL.md §38).
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models import ContentItem, ContentStatus, Source
from modules.ingestion.deduplicator import dedupe_batch, find_canonical, record_occurrence
from modules.ingestion.normalizer import canonicalize_url, content_hash
from modules.ingestion.sources.base import RawItem
from modules.ingestion.sources.base import Source as SourcePlugin
from modules.ingestion.sources.github import GitHubSource
from modules.ingestion.sources.hackernews import HackerNewsSource
from modules.ingestion.sources.rss import RSSSource

logger = logging.getLogger("radar.ingestion.collector")

PLUGIN_TYPES = {
    "rss": RSSSource,
    "hackernews": HackerNewsSource,
    "github": GitHubSource,
}


def build_plugin(row: Source) -> SourcePlugin:
    plugin_cls = PLUGIN_TYPES.get(row.source_type)
    if plugin_cls is None:
        raise ValueError(f"Unknown source type: {row.source_type}")
    return plugin_cls(name=row.name, url=row.url, config=row.config)


async def run_collection(db: AsyncSession) -> dict[str, int]:
    result = await db.execute(select(Source).where(Source.enabled.is_(True)))
    rows = list(result.scalars().all())
    stats = {"sources": len(rows), "fetched": 0, "new": 0, "duplicates": 0, "failed": 0}

    for row in rows:
        try:
            plugin = build_plugin(row)
            raw_items: list[RawItem] = await plugin.fetch()
        except Exception as exc:
            stats["failed"] += 1
            logger.error("Source %s failed: %s", row.name, exc)
            continue

        raw_items = dedupe_batch(raw_items)[: settings.max_items_per_source_run]
        stats["fetched"] += len(raw_items)

        for raw in raw_items:
            canonical = canonicalize_url(raw.url)
            chash = content_hash(raw.title, canonical)
            existing = await find_canonical(
                db, content_hash=chash, external_id=raw.external_id, source_id=row.id
            )
            if existing is not None:
                stats["duplicates"] += 1
                if existing.source_id != row.id or existing.external_id != raw.external_id:
                    await record_occurrence(db, existing, source_id=row.id, url=raw.url)
                continue

            db.add(
                ContentItem(
                    source_id=row.id,
                    external_id=raw.external_id,
                    title=raw.title,
                    url=raw.url,
                    canonical_url=canonical,
                    author=raw.author,
                    description=raw.description,
                    content=raw.content,
                    published_at=raw.published_at,
                    language="en",
                    content_hash=chash,
                    status=ContentStatus.discovered.value,
                )
            )
            stats["new"] += 1

        await db.execute(
            update(Source).where(Source.id == row.id).values(last_collected_at=datetime.now(UTC))
        )
        logger.info("Source %s: fetched=%d", row.name, len(raw_items))

    await db.commit()
    logger.info("Collection complete: %s", stats)
    return stats


async def ensure_seed_sources(db: AsyncSession) -> None:
    """Seed a minimal default source set on first run (DB-stored, GOAL.md §11)."""
    count = await db.scalar(select(func.count()).select_from(Source))
    if count:
        return
    defaults = [
        Source(
            name="hacker-news-front-page",
            source_type="hackernews",
            url="https://news.ycombinator.com/",
            config={"min_score": 150, "limit": 25},
            quality_weight=0.55,
        ),
        Source(
            name="github-releases",
            source_type="github",
            url="https://api.github.com/",
            config={
                "repos": [
                    "fastapi/fastapi",
                    "langchain-ai/langchain",
                    "ollama/ollama",
                    "openai/openai-python",
                ]
            },
            quality_weight=0.85,
        ),
    ]
    db.add_all(defaults)
    await db.commit()
    logger.info("Seeded %d default sources", len(defaults))
