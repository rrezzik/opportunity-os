import json

from fastapi.testclient import TestClient

from app.main import app
from app.services import FELLOW_URL, build_cleaned_source, normalize_approved_url


client = TestClient(app)


def evidence(value: str | None, quote: str | None = None) -> dict:
    return {"value": value, "quote": quote}


def valid_extraction() -> dict:
    return {
        "company": evidence("Fellow", "Company: Fellow"),
        "title": evidence("Software Engineer", "Title: Software Engineer"),
        "location": evidence("Canada", "Locations: Canada"),
        "compensation": evidence(None),
        "employment_type": evidence("Full time", "Employment types: full time"),
        "posting_date": evidence("2026-10-15", "Posted at: 2026-10-15"),
        "work_arrangement": evidence("Remote", "remote"),
        "source_identifier": "97059938-software-engineer",
        "source_url": FELLOW_URL,
        "responsibilities": [],
        "required_qualifications": [],
        "preferred_qualifications": [],
        "technologies": [],
        "seniority": evidence(None),
        "suggested_role_family": evidence("Software engineering", "Software Engineer"),
    }


def test_normalizes_approved_url_fragment() -> None:
    assert normalize_approved_url(f"{FELLOW_URL}#content") == FELLOW_URL


def test_rejects_unapproved_source_before_fetch() -> None:
    response = client.post("/api/source", json={"url": "http://127.0.0.1/private"})
    assert response.status_code == 400
    assert "approved Fellow and Multiview" in response.json()["detail"]


def test_accepts_valid_extraction() -> None:
    response = client.post(
        "/api/extractions/validate",
        json={
            "expected_source_url": FELLOW_URL,
            "raw_json": json.dumps(valid_extraction()),
        },
    )
    assert response.status_code == 200
    assert response.json()["extraction"]["company"]["value"] == "Fellow"


def test_rejects_malformed_extraction() -> None:
    response = client.post(
        "/api/extractions/validate",
        json={"expected_source_url": FELLOW_URL, "raw_json": "not json"},
    )
    assert response.status_code == 422


def test_rejects_mismatched_source_identifier() -> None:
    extraction = valid_extraction()
    extraction["source_identifier"] = "different-posting"
    response = client.post(
        "/api/extractions/validate",
        json={
            "expected_source_url": FELLOW_URL,
            "raw_json": json.dumps(extraction),
        },
    )
    assert response.status_code == 422
    assert "source identifier" in response.json()["detail"]


def test_extracts_job_data_from_next_payload() -> None:
    job = {
        "id": 97059938,
        "slug": "97059938-software-engineer",
        "title": "Software Engineer",
        "organization": {"name": "Fellow"},
        "locations": [{"name": "Canada"}],
        "employmentTypes": ["full_time"],
        "postedAt": "2026-10-15T12:49:10.996Z",
        "description": "<p>Build reliable software for real customers.</p>" * 4,
    }
    payload = {
        "props": {
            "pageProps": {
                "initialState": {"jobs": {"currentJob": job}},
            }
        }
    }
    html = (
        '<script id="__NEXT_DATA__" type="application/json">'
        f"{json.dumps(payload)}"
        "</script>"
    )

    source_identifier, cleaned = build_cleaned_source(html, FELLOW_URL)

    assert source_identifier == "97059938-software-engineer"
    assert "Company: Fellow" in cleaned
    assert "Build reliable software for real customers." in cleaned
