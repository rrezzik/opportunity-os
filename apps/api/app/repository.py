import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from .db_models import ExtractionDraft, PostingCapture
from .models import PostingExtraction, SourcePackage


def create_capture(session: Session, source: SourcePackage) -> PostingCapture:
    capture = PostingCapture(
        source_url=source.source_url,
        source_identifier=source.source_identifier,
        captured_at=datetime.now(timezone.utc),
        raw_source=source.raw_source,
        canonical_cleaned_source=source.cleaned_source,
        source_format_version=source.source_format_version,
        content_sha256=hashlib.sha256(source.raw_source.encode()).hexdigest(),
    )
    session.add(capture)
    session.commit()
    return capture


def create_extraction_draft(
    session: Session,
    capture: PostingCapture,
    extraction: PostingExtraction,
) -> ExtractionDraft:
    draft = ExtractionDraft(
        capture_id=capture.id,
        extraction_schema_version=extraction.schema_version,
        structured_json=extraction.model_dump(mode="json"),
        status="provisional",
        created_at=datetime.now(timezone.utc),
    )
    session.add(draft)
    session.commit()
    return draft
