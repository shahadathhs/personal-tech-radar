"""Initial schema: users, profiles, interests, sources, content, digests, feedback

Revision ID: 7c1a0f52b3d4
Revises:
Create Date: 2026-09-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql as pg

revision: str = "7c1a0f52b3d4"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID = pg.UUID(as_uuid=True)
NOW = sa.text("now()")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "user_profiles",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column(
            "role", sa.String(120), nullable=False, server_default="software engineer"
        ),
        sa.Column("experience_level", sa.String(40), nullable=False, server_default="senior"),
        sa.Column(
            "excluded_topics", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column(
            "preferred_sources", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")
        ),
        sa.Column("digest_time", sa.String(5), nullable=False, server_default="19:00"),
        sa.Column("digest_length", sa.String(10), nullable=False, server_default="normal"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "interests",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("parent_id", UUID, sa.ForeignKey("interests.id"), nullable=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("weight", sa.Float, nullable=False, server_default="1"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "sources",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("name", sa.String(200), nullable=False, unique=True),
        sa.Column("source_type", sa.String(20), nullable=False, server_default="rss"),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("config", pg.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("quality_weight", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("rate_limit_seconds", sa.Integer, nullable=False, server_default="60"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("last_collected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "content_items",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("source_id", UUID, sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("external_id", sa.String(500), nullable=False),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("canonical_url", sa.String(2000), nullable=False),
        sa.Column("author", sa.String(300), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "discovered_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW
        ),
        sa.Column("language", sa.String(10), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="discovered"),
        sa.Column("shown_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_shown_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )
    op.create_index("ix_content_items_canonical_url", "content_items", ["canonical_url"])
    op.create_index("ix_content_items_content_hash", "content_items", ["content_hash"])
    op.create_index("ix_content_items_published_at", "content_items", ["published_at"])
    op.create_index("ix_content_items_status", "content_items", ["status"])
    op.create_index(
        "uq_content_items_source_external",
        "content_items",
        ["source_id", "external_id"],
        unique=True,
    )

    op.create_table(
        "source_occurrences",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "content_item_id", UUID, sa.ForeignKey("content_items.id"), nullable=False
        ),
        sa.Column("source_id", UUID, sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("external_url", sa.String(2000), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "ai_analyses",
        sa.Column("id", UUID, primary_key=True),
        sa.Column(
            "content_item_id", UUID, sa.ForeignKey("content_items.id"), nullable=False, unique=True
        ),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("category", sa.String(60), nullable=False),
        sa.Column("subcategory", sa.String(60), nullable=True),
        sa.Column("topics", pg.JSONB, nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("importance", sa.Float, nullable=False, server_default="0"),
        sa.Column("user_relevance", sa.Float, nullable=False, server_default="0"),
        sa.Column("novelty", sa.Float, nullable=False, server_default="0"),
        sa.Column("actionability", sa.Float, nullable=False, server_default="0"),
        sa.Column("credibility", sa.Float, nullable=False, server_default="0"),
        sa.Column("is_breaking", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("is_duplicate", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("why_it_matters", sa.Text, nullable=True),
        sa.Column("why_user_should_care", sa.Text, nullable=True),
        sa.Column("recommended_action", sa.String(20), nullable=False, server_default="read"),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "digests",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("digest_date", sa.Date, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reading_time_minutes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.UniqueConstraint("user_id", "digest_date", name="uq_digests_user_date"),
    )
    op.create_index("ix_digests_user_created_at", "digests", ["user_id", "created_at"])

    op.create_table(
        "digest_items",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("digest_id", UUID, sa.ForeignKey("digests.id"), nullable=False),
        sa.Column(
            "content_item_id", UUID, sa.ForeignKey("content_items.id"), nullable=False
        ),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("section", sa.String(20), nullable=False, server_default="category"),
        sa.Column("category", sa.String(60), nullable=True),
        sa.Column("final_score", sa.Float, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )

    op.create_table(
        "feedback",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column(
            "content_item_id", UUID, sa.ForeignKey("content_items.id"), nullable=False
        ),
        sa.Column("feedback_type", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
        sa.UniqueConstraint(
            "user_id", "content_item_id", "feedback_type", name="uq_feedback_user_item_type"
        ),
    )

    op.create_table(
        "notifications",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("digest_id", UUID, sa.ForeignKey("digests.id"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False, server_default="telegram"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error", sa.Text, nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=NOW),
    )


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("feedback")
    op.drop_table("digest_items")
    op.drop_index("ix_digests_user_created_at", table_name="digests")
    op.drop_table("digests")
    op.drop_table("ai_analyses")
    op.drop_table("source_occurrences")
    op.drop_index("uq_content_items_source_external", table_name="content_items")
    op.drop_index("ix_content_items_status", table_name="content_items")
    op.drop_index("ix_content_items_published_at", table_name="content_items")
    op.drop_index("ix_content_items_content_hash", table_name="content_items")
    op.drop_index("ix_content_items_canonical_url", table_name="content_items")
    op.drop_table("content_items")
    op.drop_table("sources")
    op.drop_table("interests")
    op.drop_table("user_profiles")
    op.drop_table("users")
