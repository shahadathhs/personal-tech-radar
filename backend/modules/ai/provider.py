"""AI provider interface. The system MUST NOT hardcode a provider (GOAL.md §19)."""

from typing import Protocol

from modules.ai.schemas import ContentAnalysis


class AIProvider(Protocol):
    async def analyze(
        self,
        *,
        title: str,
        description: str | None,
        content: str | None,
        user_context: str,
    ) -> ContentAnalysis:
        """Analyze one content item against the user's interest context."""
        ...
