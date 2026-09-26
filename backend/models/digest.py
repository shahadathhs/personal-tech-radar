import enum
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class DigestStatus(str, enum.Enum):
    pending = "pending"
    generated = "generated"
    sent = "sent"
    failed = "failed"


class DigestSection(str, enum.Enum):
    top_story = "top_story"
    category = "category"
    worth_exploring = "worth_exploring"
    learning = "learning"


class Digest(Base):
    __tablename__ = "digests"
    __table_args__ = (
        Index("ix_digests_user_created_at", "user_id", "created_at"),
        UniqueConstraint("user_id", "digest_date", name="uq_digests_user_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    digest_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default=DigestStatus.pending.value)
    reading_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items = relationship(
        "DigestItem",
        back_populates="digest",
        cascade="all, delete-orphan",
        order_by="DigestItem.position",
    )


class DigestItem(Base):
    __tablename__ = "digest_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    digest_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("digests.id"))
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"))
    position: Mapped[int] = mapped_column(Integer)
    section: Mapped[str] = mapped_column(String(20), default=DigestSection.category.value)
    category: Mapped[str | None] = mapped_column(String(60))
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    digest = relationship("Digest", back_populates="items")
    content_item = relationship("ContentItem")
