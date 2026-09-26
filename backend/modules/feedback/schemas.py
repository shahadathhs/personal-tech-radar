from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from models.feedback import FeedbackType


class FeedbackIn(BaseModel):
    content_item_id: UUID
    feedback_type: FeedbackType


class FeedbackOut(BaseModel):
    id: UUID
    content_item_id: UUID
    feedback_type: str
    created_at: datetime


class SavedItemOut(BaseModel):
    content_item_id: UUID
    title: str
    url: str
    source_name: str | None
    saved_at: datetime
