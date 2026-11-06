"""Create posting captures and provisional extraction drafts.

Revision ID: 20261106_01
Revises:
Create Date: 2026-11-06
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20261106_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "posting_captures",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_identifier", sa.String(length=255), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_source", sa.Text(), nullable=False),
        sa.Column("canonical_cleaned_source", sa.Text(), nullable=False),
        sa.Column("source_format_version", sa.String(length=20), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "extraction_drafts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("capture_id", sa.Uuid(), nullable=False),
        sa.Column("extraction_schema_version", sa.String(length=20), nullable=False),
        sa.Column("structured_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["capture_id"], ["posting_captures.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_extraction_drafts_capture_id"),
        "extraction_drafts",
        ["capture_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_extraction_drafts_capture_id"), table_name="extraction_drafts"
    )
    op.drop_table("extraction_drafts")
    op.drop_table("posting_captures")
