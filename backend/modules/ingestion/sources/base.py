"""Source plugin interface (GOAL.md §10)."""

import abc
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RawItem:
    source_name: str
    source_type: str
    external_id: str
    title: str
    url: str
    author: str | None = None
    description: str | None = None
    content: str | None = None
    published_at: datetime | None = None
    # Engagement signals — one ranking input, never importance itself.
    score: int = 0
    comment_count: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


class Source(abc.ABC):
    source_name: str
    source_type: str
    rate_limit_seconds: int = 60
    enabled: bool = True

    def __init__(self, *, name: str, url: str, config: dict[str, Any] | None = None) -> None:
        self.source_name = name
        self.url = url
        self.config = config or {}

    @abc.abstractmethod
    async def fetch(self) -> list[RawItem]: ...
