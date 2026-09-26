"""Digest formatting — Telegram message, professional briefing tone (GOAL.md §46)."""

from models import AIAnalysis, ContentItem
from models.digest import DigestSection

SECTION_LABELS = {
    DigestSection.top_story.value: "🔥 TOP STORIES",
    DigestSection.category.value: "📡 DEVELOPMENTS",
    DigestSection.worth_exploring.value: "⭐ WORTH EXPLORING",
    DigestSection.learning.value: "📚 ONE THING TO LEARN",
}

CATEGORY_EMOJI = {
    "AI": "🤖",
    "Developer Tools": "🛠",
    "Infrastructure": "☁️",
    "Security": "🔒",
    "Research": "🔬",
    "Industry": "🚀",
}


def format_telegram(*, digest_date: str, reading_time: int, rows: list[tuple]) -> str:
    """Render the digest as a Telegram-ready text briefing.

    rows: list of (DigestItem, ContentItem, AIAnalysis) in digest order.
    """
    lines = [f"🧠 YOUR TECH RADAR — {digest_date}", ""]

    current_section = None
    for digest_item, content, analysis in rows:
        if digest_item.section != current_section:
            current_section = digest_item.section
            label = SECTION_LABELS.get(current_section, "📡 DEVELOPMENTS")
            lines += ["────────────────", label, ""]

        lines.extend(_format_item(digest_item.position + 1, content, analysis))

    lines += ["────────────────", f"⏱ ~{reading_time} min read"]
    return "\n".join(lines)


def _format_item(position: int, content: ContentItem, analysis: AIAnalysis) -> list[str]:
    emoji = CATEGORY_EMOJI.get(analysis.category, "•")
    source_name = content.source.name if content.source is not None else "unknown"
    lines = [
        f"{position}. {content.title}",
        f"{emoji} {analysis.category} · via {source_name}",
    ]
    if analysis.summary:
        lines += ["", analysis.summary]
    if analysis.why_it_matters:
        lines += ["", f"Why it matters: {analysis.why_it_matters}"]
    if analysis.why_user_should_care:
        lines += ["", f"Why you should care: {analysis.why_user_should_care}"]
    lines += ["", f"Source: {content.canonical_url}", ""]
    return lines
