from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from models.source import SourceType


class SourceIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    source_type: SourceType = SourceType.rss
    url: str = Field(min_length=1, max_length=2000)
    config: dict[str, Any] = Field(default_factory=dict)
    quality_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    rate_limit_seconds: int = Field(default=60, ge=0)
    enabled: bool = True


class SourcePatch(BaseModel):
    quality_weight: float | None = Field(default=None, ge=0.0, le=1.0)
    rate_limit_seconds: int | None = Field(default=None, ge=0)
    enabled: bool | None = None
    config: dict[str, Any] | None = None


class SourceOut(BaseModel):
    id: UUID
    name: str
    source_type: str
    url: str
    config: dict[str, Any]
    quality_weight: float
    rate_limit_seconds: int
    enabled: bool
    last_collected_at: datetime | None
