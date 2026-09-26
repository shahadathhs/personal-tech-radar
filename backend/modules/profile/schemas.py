from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from models.user import DigestLength


class InterestIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    parent_name: str | None = None
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    enabled: bool = True


class InterestOut(BaseModel):
    id: UUID
    name: str
    parent_name: str | None
    weight: float
    enabled: bool


class ProfileOut(BaseModel):
    email: str
    timezone: str
    role: str
    experience_level: str
    digest_time: str
    digest_length: str
    excluded_topics: list[str]
    preferred_sources: list[str]
    interests: list[InterestOut]


class ProfileUpdate(BaseModel):
    role: str | None = None
    experience_level: str | None = None
    digest_time: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    digest_length: DigestLength | None = None
    timezone: str | None = None
    excluded_topics: list[str] | None = None
    preferred_sources: list[str] | None = None


class ProfileOutWithTimestamps(ProfileOut):
    updated_at: datetime | None = None
