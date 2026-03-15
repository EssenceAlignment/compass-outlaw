"""
tests/test_routes.py – Integration tests for POST /api/generate_pleading.
"""

import json

import pytest

from backend.app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helper payload
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "identity": {
        "filer_name": "Jane Doe",
        "filer_address": "123 Main St, Los Angeles, CA 90001",
        "case_number": "24STCV00001",
        "case_title": "Doe v. Smith",
        "court": "Superior Court of California, County of Los Angeles",
    },
    "geo": {
        "lines_per_page": 28,
        "margin_top": 1.0,
        "margin_bottom": 1.0,
        "margin_left": 1.5,
        "margin_right": 0.5,
        "font_size": 12,
    },
    "body_md": (
        "# COMPLAINT FOR DAMAGES\n\n"
        "**COMES NOW** Plaintiff Jane Doe and alleges as follows:\n\n"
        "1. Plaintiff is a resident of Los Angeles County.\n"
        "2. Defendant resides at 456 Oak Ave, Los Angeles, CA 90002.\n"
    ),
}


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------

def test_generate_pleading_returns_pdf(client):
    """A well-formed request must return a PDF file (200)."""
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(VALID_PAYLOAD),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.content_type == "application/pdf"
    # PDF magic bytes
    assert resp.data[:4] == b"%PDF"


def test_generate_pleading_content_disposition(client):
    """Response must carry Content-Disposition attachment header."""
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(VALID_PAYLOAD),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert "pleading.pdf" in resp.headers.get("Content-Disposition", "")


def test_generate_pleading_verify_report_header(client):
    """Successful response must include the X-Verify-Report header."""
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(VALID_PAYLOAD),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert "X-Verify-Report" in resp.headers


def test_generate_pleading_empty_body_md(client):
    """An empty markdown body should still produce a PDF."""
    payload = {**VALID_PAYLOAD, "body_md": ""}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.data[:4] == b"%PDF"


def test_generate_pleading_default_geo(client):
    """Omitting geo fields should fall back to defaults without error."""
    payload = {**VALID_PAYLOAD, "geo": {}}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Validation errors (400)
# ---------------------------------------------------------------------------

def test_missing_identity_returns_400(client):
    payload = {"geo": VALID_PAYLOAD["geo"], "body_md": VALID_PAYLOAD["body_md"]}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "identity" in resp.get_json()["error"]


def test_missing_geo_returns_400(client):
    payload = {"identity": VALID_PAYLOAD["identity"], "body_md": VALID_PAYLOAD["body_md"]}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "geo" in resp.get_json()["error"]


def test_missing_body_md_returns_400(client):
    payload = {"identity": VALID_PAYLOAD["identity"], "geo": VALID_PAYLOAD["geo"]}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
    assert "body_md" in resp.get_json()["error"]


def test_invalid_json_returns_400(client):
    resp = client.post(
        "/api/generate_pleading",
        data="not json",
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_identity_not_dict_returns_400(client):
    payload = {**VALID_PAYLOAD, "identity": "not a dict"}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_geo_not_dict_returns_400(client):
    payload = {**VALID_PAYLOAD, "geo": "not a dict"}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_body_md_not_string_returns_400(client):
    payload = {**VALID_PAYLOAD, "body_md": 42}
    resp = client.post(
        "/api/generate_pleading",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert resp.status_code == 400
