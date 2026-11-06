from uuid import UUID

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.orm import Session

from .database import get_session
from .db_models import ExtractionDraft, PostingCapture
from .models import (
    CaptureResponse,
    ExtractionSubmission,
    PostingExtraction,
    SourceRequest,
    ValidationResponse,
)
from .repository import create_capture, create_extraction_draft
from .services import APPROVED_SOURCES, build_prompt, fetch_source_package, validate_extraction


def capture_response(capture: PostingCapture) -> CaptureResponse:
    return CaptureResponse(
        id=capture.id,
        source_format_version=capture.source_format_version,
        source_url=capture.source_url,
        source_identifier=capture.source_identifier,
        source_label=APPROVED_SOURCES[capture.source_url],
        captured_at=capture.captured_at,
        raw_source=capture.raw_source,
        cleaned_source=capture.canonical_cleaned_source,
        content_sha256=capture.content_sha256,
        prompt=build_prompt(
            capture.source_url,
            capture.source_identifier,
            capture.canonical_cleaned_source,
        ),
    )


def draft_response(draft: ExtractionDraft) -> ValidationResponse:
    return ValidationResponse(
        id=draft.id,
        capture_id=draft.capture_id,
        extraction_schema_version=draft.extraction_schema_version,
        status=draft.status,
        created_at=draft.created_at,
        extraction=PostingExtraction.model_validate(draft.structured_json),
    )


def create_app() -> FastAPI:
    application = FastAPI(title="Opportunity OS API", version="0.2.0")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post("/api/source", response_model=CaptureResponse)
    async def source(
        request: SourceRequest,
        session: Session = Depends(get_session),
    ) -> CaptureResponse:
        try:
            package = await fetch_source_package(request.url)
            return capture_response(create_capture(session, package))
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        except httpx.HTTPError as error:
            raise HTTPException(
                status_code=502,
                detail="The approved posting could not be fetched.",
            ) from error

    @application.get("/api/captures/{capture_id}", response_model=CaptureResponse)
    async def get_capture(
        capture_id: UUID,
        session: Session = Depends(get_session),
    ) -> CaptureResponse:
        capture = session.get(PostingCapture, capture_id)
        if capture is None:
            raise HTTPException(status_code=404, detail="Capture not found.")
        return capture_response(capture)

    @application.post(
        "/api/extractions/validate",
        response_model=ValidationResponse,
    )
    async def extraction(
        request: ExtractionSubmission,
        session: Session = Depends(get_session),
    ) -> ValidationResponse:
        capture = session.get(PostingCapture, request.capture_id)
        if capture is None:
            raise HTTPException(status_code=404, detail="Capture not found.")
        try:
            validated = validate_extraction(
                request.raw_json,
                capture.source_url,
                capture.source_identifier,
                capture.canonical_cleaned_source,
            )
        except (ValidationError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
        return draft_response(create_extraction_draft(session, capture, validated))

    @application.get(
        "/api/extractions/{extraction_id}",
        response_model=ValidationResponse,
    )
    async def get_extraction(
        extraction_id: UUID,
        session: Session = Depends(get_session),
    ) -> ValidationResponse:
        draft = session.get(ExtractionDraft, extraction_id)
        if draft is None:
            raise HTTPException(status_code=404, detail="Extraction draft not found.")
        return draft_response(draft)

    return application


app = create_app()
