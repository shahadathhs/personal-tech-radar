import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class SourceType(str, enum.Enum):
    rss = "rss"
    github = "github"
    hackernews = "hackernews"


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    source_type: Mapped[str] = mapped_column(String(20), default=SourceType.rss.value)
    url: Mapped[str] = mapped_column(String(2000))
    # Source-type specific config (e.g. github repo/topic list, HN min score).
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    # Quality weight in [0, 1] — one ranking signal, not a truth guarantee.
    quality_weight: Mapped[float] = mapped_column(Float, default=0.5)
    rate_limit_seconds: Mapped[int] = mapped_column(default=60)
    enabled: Mapped[bool] = mapped_column(default=True)
    last_collected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
