import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class FeedbackType(str, enum.Enum):
    useful = "useful"
    not_useful = "not_useful"
    save = "save"
    less_like = "less_like"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "content_item_id", "feedback_type", name="uq_feedback_user_item_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"))
    feedback_type: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    content_item = relationship("ContentItem")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    digest_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("digests.id"))
    channel: Mapped[str] = mapped_column(String(20), default="telegram")
    status: Mapped[str] = mapped_column(String(20), default=NotificationStatus.pending.value)
    error: Mapped[str | None] = mapped_column(String)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
