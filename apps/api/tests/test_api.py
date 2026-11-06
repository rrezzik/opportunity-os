import json
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import (
    FELLOW_URL,
    MULTIVIEW_URL,
    build_cleaned_source,
    normalize_approved_url,
    validate_extraction,
)


FIXTURES = Path(__file__).parent / "fixtures"
client = TestClient(app)


def fixture_source() -> tuple[str, str, str]:
    raw_source = (FIXTURES / "fellow_minimized.html").read_text()
    source_identifier, cleaned_source = build_cleaned_source(raw_source, FELLOW_URL)
    return raw_source, source_identifier, cleaned_source


def valid_extraction() -> dict:
    return json.loads((FIXTURES / "fellow_extraction_v1.json").read_text())


def validation_payload(extraction: dict | None = None) -> dict:
    _, _, cleaned_source = fixture_source()
    return {
        "expected_source_url": FELLOW_URL,
        "canonical_cleaned_source": cleaned_source,
        "raw_json": json.dumps(extraction or valid_extraction()),
    }


def test_normalizes_approved_url_fragment() -> None:
    assert normalize_approved_url(f"{FELLOW_URL}#content") == FELLOW_URL


def test_rejects_query_parameters() -> None:
    with pytest.raises(ValueError, match="Query parameters"):
        normalize_approved_url(f"{FELLOW_URL}?redirect=http://127.0.0.1")


def test_rejects_unapproved_source_before_fetch() -> None:
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
    response = client.post("/api/source", json={"url": FELLOW_URL})
    assert response.status_code == 502
    assert response.json()["detail"] == "The approved posting could not be fetched."


def test_accepts_deterministic_fixture_extraction() -> None:
    response = client.post("/api/extractions/validate", json=validation_payload())
    assert response.status_code == 200
    extraction = response.json()["extraction"]
    assert extraction["schema_version"] == "1.0"
    assert extraction["company"]["value"] == "Fellow"


@pytest.mark.parametrize(
    "unsupported_text",
    [
        "Company: Imaginary Company",
        "company: Fellow",
        "Build reliable software React and Python.",
    ],
)
def test_rejects_non_verbatim_supporting_source_text(
    unsupported_text: str,
) -> None:
    extraction = valid_extraction()
    extraction["company"]["supporting_source_text"] = unsupported_text
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422
    assert "does not occur verbatim" in response.json()["detail"]


def test_rejects_malformed_extraction() -> None:
    payload = validation_payload()
    payload["raw_json"] = "not json"
    response = client.post("/api/extractions/validate", json=payload)
    assert response.status_code == 422


def test_rejects_wrong_schema_version() -> None:
    extraction = valid_extraction()
    extraction["schema_version"] = "2.0"
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422


def test_rejects_extra_fields() -> None:
    extraction = valid_extraction()
    extraction["unversioned_extra"] = "not allowed"
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422


def test_rejects_mismatched_source_url() -> None:
    extraction = valid_extraction()
    extraction["source_url"] = MULTIVIEW_URL
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422
    assert "source URL" in response.json()["detail"]


def test_rejects_mismatched_source_identifier() -> None:
    extraction = valid_extraction()
    extraction["source_identifier"] = "different-posting"
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422
    assert "source identifier" in response.json()["detail"]


def test_rejects_cleaned_source_without_expected_provenance() -> None:
    payload = validation_payload()
    payload["canonical_cleaned_source"] = "Company: Fellow\nTitle: Software Engineer"
    response = client.post("/api/extractions/validate", json=payload)
    assert response.status_code == 422
    assert "cleaned source does not match" in response.json()["detail"]


def test_rejects_value_without_supporting_source_text() -> None:
    extraction = valid_extraction()
    extraction["company"]["supporting_source_text"] = None
    response = client.post(
        "/api/extractions/validate",
        json=validation_payload(extraction),
    )
    assert response.status_code == 422
    assert "require supporting source text" in response.json()["detail"]


def test_preserves_raw_and_cleaned_source_as_distinct_values() -> None:
    raw_source, source_identifier, cleaned_source = fixture_source()
    assert source_identifier == "97059938-software-engineer"
    assert "<script" in raw_source
    assert "<script" not in cleaned_source
    assert "Company: Fellow" in cleaned_source
    assert "Build reliable software for real customers." in cleaned_source


def test_validates_fixture_directly_without_network_or_model() -> None:
    _, _, cleaned_source = fixture_source()
    extraction = validate_extraction(
        json.dumps(valid_extraction()),
        FELLOW_URL,
        cleaned_source,
    )
    assert extraction.company.supporting_source_text == "Company: Fellow"
