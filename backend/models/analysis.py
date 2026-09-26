import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class RecommendedAction(str, enum.Enum):
    read = "read"
    investigate = "investigate"
    bookmark = "bookmark"
    ignore = "ignore"


class AIAnalysis(Base):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("content_items.id"), unique=True)
    summary: Mapped[str] = mapped_column(String)
    category: Mapped[str] = mapped_column(String(60))
    subcategory: Mapped[str | None] = mapped_column(String(60))
    topics: Mapped[list[str]] = mapped_column(JSONB, default=list)
    importance: Mapped[float] = mapped_column(Float, default=0.0)
    user_relevance: Mapped[float] = mapped_column(Float, default=0.0)
    novelty: Mapped[float] = mapped_column(Float, default=0.0)
    actionability: Mapped[float] = mapped_column(Float, default=0.0)
    credibility: Mapped[float] = mapped_column(Float, default=0.0)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    why_it_matters: Mapped[str | None] = mapped_column(String)
    why_user_should_care: Mapped[str | None] = mapped_column(String)
    recommended_action: Mapped[str] = mapped_column(
        String(20), default=RecommendedAction.read.value
    )
    model: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    content_item = relationship("ContentItem", back_populates="analysis")
