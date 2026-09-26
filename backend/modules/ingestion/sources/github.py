"""GitHub source via the official REST API (GOAL.md §11).

Tracks releases for configured repos. Config example:
  {"repos": ["fastapi/fastapi", "langchain-ai/langchain"], "token": "ghp_..."}
"""

import logging
from datetime import UTC, datetime

import httpx

from modules.ingestion.sources.base import RawItem, Source

logger = logging.getLogger("radar.ingestion.github")
API = "https://api.github.com"


class GitHubSource(Source):
    source_type = "github"

    async def fetch(self) -> list[RawItem]:
        repos: list[str] = self.config.get("repos", [])
        token: str = self.config.get("token", "")
        headers = {"Accept": "application/vnd.github+json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        items: list[RawItem] = []
        async with httpx.AsyncClient(timeout=30, headers=headers) as client:
            for repo in repos[:25]:
                try:
                    releases = await self._fetch_releases(client, repo)
                except httpx.HTTPError as exc:
                    # One repo failing must not break the source (GOAL.md §38).
                    logger.warning("GitHub releases fetch failed for %s: %s", repo, exc)
                    continue
                items.extend(releases)
        return items

    async def _fetch_releases(self, client: httpx.AsyncClient, repo: str) -> list[RawItem]:
        resp = await client.get(f"{API}/repos/{repo}/releases", params={"per_page": 5})
        resp.raise_for_status()
        items: list[RawItem] = []
        for rel in resp.json():
            published = None
            if rel.get("published_at"):
                published = datetime.fromisoformat(rel["published_at"].replace("Z", "+00:00"))
            items.append(
                RawItem(
                    source_name=self.source_name,
                    source_type=self.source_type,
                    external_id=str(rel["id"]),
                    title=f"{repo} {rel.get('tag_name', '')}: {rel.get('name') or 'release'}"[
                        :1000
                    ],
                    url=rel.get("html_url", f"https://github.com/{repo}/releases"),
                    author=rel.get("author", {}).get("login"),
                    description=(rel.get("body") or "")[:2000],
                    published_at=published or datetime.now(UTC),
                )
            )
        return items
