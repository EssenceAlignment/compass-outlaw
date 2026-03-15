"""
routes.py – Flask API blueprint for Compass Outlaw.

Registers the POST /api/generate_pleading endpoint which:

1. Accepts a JSON payload with ``identity``, ``geo``, and ``body_md`` keys.
2. Calls ``renderer.compile_pleading`` to produce raw PDF bytes.
3. Passes those bytes through ``pdfa.apply_pdfa`` for PDF/A-2b compliance
   and metadata sanitisation.
4. Runs ``verify.verify`` to confirm the geometric checksum.
5. Returns the PDF file on success (200) or a JSON error on failure (500).
"""

from flask import Blueprint, Response, jsonify, request

from backend.pdfa import apply_pdfa
from backend.renderer import compile_pleading
from backend.verify import verify

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/generate_pleading", methods=["POST"])
def generate_pleading() -> Response:
    """
    Generate a PDF/A-2b legal pleading document.

    Request body (JSON)
    -------------------
    identity : dict
        Filer and case information (``filer_name``, ``filer_address``,
        ``case_number``, ``case_title``, ``court``).
    geo : dict
        Grid geometry overrides (see ``renderer.DEFAULT_GEO`` for accepted
        keys and their defaults).
    body_md : str
        Markdown-formatted body text of the pleading.

    Responses
    ---------
    200 application/pdf
        The compiled, PDF/A-2b–compliant pleading document.
    400 application/json
        ``{"error": "<reason>"}`` when the request payload is malformed.
    500 application/json
        ``{"error": "Verification failed", "report": "<details>"}`` when
        the geometric checksum does not pass.
    """
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    identity = payload.get("identity")
    geo = payload.get("geo")
    body_md = payload.get("body_md")

    if identity is None or not isinstance(identity, dict):
        return jsonify({"error": "'identity' must be a JSON object."}), 400
    if geo is None or not isinstance(geo, dict):
        return jsonify({"error": "'geo' must be a JSON object."}), 400
    if body_md is None or not isinstance(body_md, str):
        return jsonify({"error": "'body_md' must be a string."}), 400

    # Step 1 – compile
    pdf_bytes = compile_pleading(identity, geo, body_md)

    # Step 2 – PDF/A-2b compliance & metadata sanitisation
    pdf_bytes = apply_pdfa(pdf_bytes)

    # Step 3 – geometric checksum verification
    result = verify(pdf_bytes)
    if not result["passed"]:
        return (
            jsonify({"error": "Verification failed", "report": result["report"]}),
            500,
        )

    return Response(
        pdf_bytes,
        status=200,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="pleading.pdf"',
            "X-Verify-Report": result["report"],
        },
    )
