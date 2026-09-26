import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class ContentStatus(str, enum.Enum):
    discovered = "discovered"
    processed = "processed"
    rejected = "rejected"
    selected = "selected"
    archived = "archived"


class ContentItem(Base):
    __tablename__ = "content_items"
    __table_args__ = (
        Index("ix_content_items_canonical_url", "canonical_url"),
        Index("ix_content_items_content_hash", "content_hash"),
        Index("ix_content_items_published_at", "published_at"),
        Index("ix_content_items_status", "status"),
        # Same external item from the same source must never duplicate.
        Index("uq_content_items_source_external", "source_id", "external_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    external_id: Mapped[str] = mapped_column(String(500))
    title: Mapped[str] = mapped_column(String(1000))
    url: Mapped[str] = mapped_column(String(2000))
    canonical_url: Mapped[str] = mapped_column(String(2000))
    author: Mapped[str | None] = mapped_column(String(300))
    description: Mapped[str | None] = mapped_column(String)
    content: Mapped[str | None] = mapped_column(String)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    discovered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    language: Mapped[str | None] = mapped_column(String(10))
    content_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default=ContentStatus.discovered.value)
    # Historical awareness (GOAL.md §34).
    shown_count: Mapped[int] = mapped_column(Integer, default=0)
    last_shown_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    source = relationship("Source")
    analysis = relationship(
        "AIAnalysis", back_populates="content_item", uselist=False, cascade="all, delete-orphan"
    )
    occurrences = relationship(
        "SourceOccurrence", back_populates="content_item", cascade="all, delete-orphan"
    )


class SourceOccurrence(Base):
    """Where else this same story appeared (dedup structure, GOAL.md §35)."""

    __tablename__ = "source_occurrences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"))
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sources.id"))
    external_url: Mapped[str] = mapped_column(String(2000))
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    content_item = relationship("ContentItem", back_populates="occurrences")
