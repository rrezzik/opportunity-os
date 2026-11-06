import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class PostingCapture(Base):
    __tablename__ = "posting_captures"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    source_url: Mapped[str] = mapped_column(Text)
    source_identifier: Mapped[str] = mapped_column(String(255))
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    raw_source: Mapped[str] = mapped_column(Text)
    canonical_cleaned_source: Mapped[str] = mapped_column(Text)
    source_format_version: Mapped[str] = mapped_column(String(20))
    content_sha256: Mapped[str] = mapped_column(String(64))

    extraction_drafts: Mapped[list["ExtractionDraft"]] = relationship(
        back_populates="capture"
    )


class ExtractionDraft(Base):
    __tablename__ = "extraction_drafts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    capture_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("posting_captures.id", ondelete="RESTRICT"), index=True
    )
    extraction_schema_version: Mapped[str] = mapped_column(String(20))
    structured_json: Mapped[dict[str, Any]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    capture: Mapped[PostingCapture] = relationship(back_populates="extraction_drafts")
