from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContentItemOut(BaseModel):
    id: UUID
    title: str
    url: str
    source_name: str | None
    status: str
    category: str | None
    summary: str | None
    published_at: datetime | None
    discovered_at: datetime


class ContentListOut(BaseModel):
    items: list[ContentItemOut]
    total: int
