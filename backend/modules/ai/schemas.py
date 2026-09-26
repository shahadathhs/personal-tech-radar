"""Structured AI analysis schemas. All provider output MUST validate here."""

from pydantic import BaseModel, Field


class ContentAnalysis(BaseModel):
    """The canonical per-item analysis record (GOAL.md §18)."""

    summary: str = Field(min_length=1)
    category: str
    subcategory: str | None = None
    topics: list[str] = Field(default_factory=list)
    importance: float = Field(ge=0.0, le=1.0)
    user_relevance: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(ge=0.0, le=1.0)
    actionability: float = Field(ge=0.0, le=1.0)
    credibility: float = Field(ge=0.0, le=1.0)
    is_breaking: bool = False
    is_duplicate: bool = False
    why_it_matters: str | None = None
    why_user_should_care: str | None = None
    recommended_action: str = "read"  # read | investigate | bookmark | ignore


class DigestIntro(BaseModel):
    """Optional polished intro line for a digest."""

    headline: str
    overview: str
