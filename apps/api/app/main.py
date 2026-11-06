import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .models import (
    ExtractionSubmission,
    SourcePackage,
    SourceRequest,
    ValidationResponse,
)
from .services import fetch_source_package, validate_extraction


app = FastAPI(title="Opportunity OS API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/source", response_model=SourcePackage)
async def source(request: SourceRequest) -> SourcePackage:
    try:
        return await fetch_source_package(request.url)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail="The approved posting could not be fetched.",
        ) from error


@app.post("/api/extractions/validate", response_model=ValidationResponse)
async def extraction(request: ExtractionSubmission) -> ValidationResponse:
    try:
        validated = validate_extraction(
            request.raw_json,
            request.expected_source_url,
            request.canonical_cleaned_source,
        )
    except (ValidationError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return ValidationResponse(extraction=validated)
