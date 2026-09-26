"""Generic RSS/Atom source (GOAL.md §11)."""

import asyncio
from datetime import UTC, datetime

import feedparser

from modules.ingestion.sources.base import RawItem, Source


class RSSSource(Source):
    source_type = "rss"

    async def fetch(self) -> list[RawItem]:
        parsed = await asyncio.to_thread(feedparser.parse, self.url)
        items: list[RawItem] = []
        limit = int(self.config.get("limit", 20))
        for entry in parsed.entries[:limit]:
            published = None
            if getattr(entry, "published_parsed", None):
                published = datetime(*entry.published_parsed[:6], tzinfo=UTC)
            items.append(
                RawItem(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    external_id=getattr(entry, "id", "") or entry.get("link", ""),
                    title=entry.get("title", "")[:1000],
                    url=entry.get("link", ""),
                    author=entry.get("author"),
                    description=entry.get("summary"),
                    published_at=published,
                )
            )
        return items
