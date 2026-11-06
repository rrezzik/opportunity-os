import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.database import SessionLocal, engine
from app.db_models import ExtractionDraft, PostingCapture
from app.main import create_app
from app.models import SourcePackage
from app.services import (
    FELLOW_URL,
    MULTIVIEW_URL,
    build_cleaned_source,
    build_prompt,
    normalize_approved_url,
    validate_extraction,
)


FIXTURES = Path(__file__).parent / "fixtures"


def fixture_source() -> tuple[str, str, str]:
    raw_source = (FIXTURES / "fellow_minimized.html").read_text()
    source_identifier, cleaned_source = build_cleaned_source(raw_source, FELLOW_URL)
    return raw_source, source_identifier, cleaned_source


def valid_extraction() -> dict:
    return json.loads((FIXTURES / "fellow_extraction_v1.json").read_text())


def validate(extraction: dict | None = None):
    _, source_identifier, cleaned_source = fixture_source()
    return validate_extraction(
        json.dumps(extraction or valid_extraction()),
        FELLOW_URL,
        source_identifier,
        cleaned_source,
    )


def test_normalizes_approved_url_fragment() -> None:
    assert normalize_approved_url(f"{FELLOW_URL}#content") == FELLOW_URL


def test_rejects_query_parameters() -> None:
    with pytest.raises(ValueError, match="Query parameters"):
        normalize_approved_url(f"{FELLOW_URL}?redirect=http://127.0.0.1")


def test_rejects_unapproved_source_before_fetch() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/api/source", json={"url": "http://127.0.0.1/private"})
    assert response.status_code == 400
    assert "approved Fellow and Multiview" in response.json()["detail"]


def test_does_not_follow_redirects(monkeypatch: pytest.MonkeyPatch) -> None:
    class RedirectingClient:
        def __init__(self, **kwargs: object) -> None:
            assert kwargs["follow_redirects"] is False

        async def __aenter__(self) -> "RedirectingClient":
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

        async def get(self, url: str) -> httpx.Response:
            return httpx.Response(
                302,
                headers={"location": "http://127.0.0.1/private"},
                request=httpx.Request("GET", url),
            )

    monkeypatch.setattr("app.services.httpx.AsyncClient", RedirectingClient)
    with TestClient(create_app()) as client:
        response = client.post("/api/source", json={"url": FELLOW_URL})
    assert response.status_code == 502
    assert response.json()["detail"] == "The approved posting could not be fetched."


def test_accepts_deterministic_fixture_extraction() -> None:
    extraction = validate()
    assert extraction.schema_version == "1.0"
    assert extraction.company.value == "Fellow"


@pytest.mark.parametrize(
    "unsupported_text",
    [
        "Company: Imaginary Company",
        "company: Fellow",
        "Build reliable software React and Python.",
    ],
)
def test_rejects_non_verbatim_supporting_source_text(unsupported_text: str) -> None:
    extraction = valid_extraction()
    extraction["company"]["supporting_source_text"] = unsupported_text
    with pytest.raises(ValueError, match="does not occur verbatim"):
        validate(extraction)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (("schema_version", "2.0"), "Input should be '1.0'"),
        (("unversioned_extra", "not allowed"), "Extra inputs are not permitted"),
        (("source_url", MULTIVIEW_URL), "source URL"),
        (("source_identifier", "different-posting"), "source identifier"),
    ],
)
def test_rejects_invalid_extraction(change: tuple[str, str], message: str) -> None:
    extraction = valid_extraction()
    extraction[change[0]] = change[1]
    with pytest.raises((ValidationError, ValueError), match=message):
        validate(extraction)


def test_rejects_malformed_extraction() -> None:
    _, source_identifier, cleaned_source = fixture_source()
    with pytest.raises(ValidationError):
        validate_extraction(
            "not json",
            FELLOW_URL,
            source_identifier,
            cleaned_source,
        )


def test_rejects_cleaned_source_without_expected_provenance() -> None:
    _, source_identifier, _ = fixture_source()
    with pytest.raises(ValueError, match="cleaned source does not match"):
        validate_extraction(
            json.dumps(valid_extraction()),
            FELLOW_URL,
            source_identifier,
            "Company: Fellow\nTitle: Software Engineer",
        )


def test_rejects_value_without_supporting_source_text() -> None:
    extraction = valid_extraction()
    extraction["company"]["supporting_source_text"] = None
    with pytest.raises(ValueError, match="require supporting source text"):
        validate(extraction)


def test_preserves_raw_and_cleaned_source_as_distinct_values() -> None:
    raw_source, source_identifier, cleaned_source = fixture_source()
    assert source_identifier == "97059938-software-engineer"
    assert "<script" in raw_source
    assert "<script" not in cleaned_source
    assert "Company: Fellow" in cleaned_source
    assert "Build reliable software for real customers." in cleaned_source


@pytest.mark.integration
def test_persists_capture_and_draft_across_application_boundaries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw_source, source_identifier, cleaned_source = fixture_source()
    package = SourcePackage(
        source_format_version="1.0",
        source_url=FELLOW_URL,
        source_identifier=source_identifier,
        source_label="Fellow Software Engineer",
        raw_source=raw_source,
        cleaned_source=cleaned_source,
        prompt=build_prompt(FELLOW_URL, source_identifier, cleaned_source),
    )

    async def fixture_fetch(url: str) -> SourcePackage:
        assert normalize_approved_url(url) == FELLOW_URL
        return package

    monkeypatch.setattr("app.main.fetch_source_package", fixture_fetch)
    with TestClient(create_app()) as first_process:
        capture_response = first_process.post("/api/source", json={"url": FELLOW_URL})
        assert capture_response.status_code == 200
        capture = capture_response.json()
        draft_response = first_process.post(
            "/api/extractions/validate",
            json={
                "capture_id": capture["id"],
                "raw_json": json.dumps(valid_extraction()),
            },
        )
        assert draft_response.status_code == 200
        draft = draft_response.json()

    engine.dispose()

    with socket.socket() as port_socket:
        port_socket.bind(("127.0.0.1", 0))
        port = port_socket.getsockname()[1]
    restarted_process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        for _ in range(50):
            try:
                health = httpx.get(f"http://127.0.0.1:{port}/health", timeout=1)
                if health.status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        else:
            pytest.fail("Restarted API process did not become healthy.")

        retrieved_capture = httpx.get(
            f"http://127.0.0.1:{port}/api/captures/{capture['id']}"
        )
        retrieved_draft = httpx.get(
            f"http://127.0.0.1:{port}/api/extractions/{draft['id']}"
        )

        assert retrieved_capture.status_code == 200
        assert retrieved_capture.json() == capture
        assert retrieved_draft.status_code == 200
        assert retrieved_draft.json() == draft
        assert draft["capture_id"] == capture["id"]
        assert draft["status"] == "provisional"
        assert draft["extraction"] == valid_extraction()
    finally:
        restarted_process.terminate()
        restarted_process.wait(timeout=5)
        with SessionLocal.begin() as session:
            persisted_draft = session.get(ExtractionDraft, UUID(draft["id"]))
            persisted_capture = session.get(PostingCapture, UUID(capture["id"]))
            if persisted_draft is not None:
                session.delete(persisted_draft)
            if persisted_capture is not None:
                session.delete(persisted_capture)
