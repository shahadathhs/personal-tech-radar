from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DigestItemOut(BaseModel):
    id: UUID
    position: int
    section: str
    category: str | None
    final_score: float
    title: str
    url: str
    source_name: str | None
    summary: str
    why_it_matters: str | None
    why_user_should_care: str | None
    recommended_action: str


class DigestOut(BaseModel):
    id: UUID
    digest_date: date
    status: str
    reading_time_minutes: int
    generated_at: datetime | None
    sent_at: datetime | None
    items: list[DigestItemOut]


class DigestListOut(BaseModel):
    id: UUID
    digest_date: date
    status: str
    reading_time_minutes: int
    item_count: int
