"""Hacker News source via the official Firebase API (GOAL.md §11)."""

from datetime import UTC

import httpx

from modules.ingestion.sources.base import RawItem, Source

API = "https://hacker-news.firebaseio.com/v0"


class HackerNewsSource(Source):
    source_type = "hackernews"

    async def fetch(self) -> list[RawItem]:
        min_score = int(self.config.get("min_score", 100))
        limit = int(self.config.get("limit", 30))
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{API}/topstories.json")
            resp.raise_for_status()
            ids = resp.json()[: limit * 3]

            items: list[RawItem] = []
            for story_id in ids:
                item = await self._fetch_item(client, story_id)
                if item is None:
                    continue
                if item.score >= min_score:
                    items.append(item)
                if len(items) >= limit:
                    break
        return items

    async def _fetch_item(self, client: httpx.AsyncClient, story_id: int) -> RawItem | None:
        resp = await client.get(f"{API}/item/{story_id}.json")
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not data or data.get("type") != "story" or not data.get("title"):
            return None
        url = data.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        from datetime import datetime

        published = datetime.fromtimestamp(data["time"], tz=UTC) if data.get("time") else None
        return RawItem(
            source_name=self.source_name,
            source_type=self.source_type,
            external_id=str(story_id),
            title=data["title"][:1000],
            url=url,
            author=data.get("by"),
            description=data.get("text"),
            published_at=published,
            score=data.get("score", 0),
            comment_count=data.get("descendants", 0),
        )
