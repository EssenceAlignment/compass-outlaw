"""
verify.py – Geometric checksum verification for compiled pleadings.

Reads the produced PDF with pypdf and verifies that every page satisfies the
declared grid geometry:

  • Page dimensions match letter size (within ±1 pt tolerance).
  • The number of content streams on each page is non-zero (document is not
    empty).
  • A SHA-256 digest of the page-layout stream bytes is recorded so that
    any post-hoc tampering can be detected.

The "geometric checksum" is the SHA-256 of the raw content-stream bytes for
each page, stored alongside the expected page-box dimensions.  If the
dimensions do not match expectations, ``passed`` is ``False`` and a
human-readable ``report`` is included.
"""

import hashlib
import io

import pypdf

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Expected page dimensions (letter, in PDF user-units = 1/72 inch)
_EXPECTED_WIDTH = 612.0
_EXPECTED_HEIGHT = 792.0
_TOLERANCE = 1.0  # points


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def verify(pdf_bytes: bytes) -> dict:
    """
    Run a geometric checksum on *pdf_bytes*.

    Parameters
    ----------
    pdf_bytes : bytes
        PDF bytes (already post-processed by ``pdfa.apply_pdfa``).

    Returns
    -------
    dict
        ``{"passed": bool, "report": str, "checksums": list[str]}``

        *passed* is ``True`` when all pages satisfy the geometric
        constraints.  *report* contains a human-readable summary.
        *checksums* is a list of per-page SHA-256 hex digests of the raw
        content-stream bytes.
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    issues: list[str] = []
    checksums: list[str] = []

    num_pages = len(reader.pages)
    if num_pages == 0:
        return {
            "passed": False,
            "report": "PDF contains no pages.",
            "checksums": [],
        }

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1

        # ---- Dimension check --------------------------------------------
        media_box = page.mediabox
        width = float(media_box.width)
        height = float(media_box.height)

        if abs(width - _EXPECTED_WIDTH) > _TOLERANCE:
            issues.append(
                f"Page {page_num}: width {width:.2f} pt deviates from "
                f"expected {_EXPECTED_WIDTH:.2f} pt "
                f"(tolerance ±{_TOLERANCE} pt)."
            )
        if abs(height - _EXPECTED_HEIGHT) > _TOLERANCE:
            issues.append(
                f"Page {page_num}: height {height:.2f} pt deviates from "
                f"expected {_EXPECTED_HEIGHT:.2f} pt "
                f"(tolerance ±{_TOLERANCE} pt)."
            )

        # ---- Content-stream checksum ------------------------------------
        raw_content = _extract_content_bytes(page)
        if not raw_content:
            issues.append(f"Page {page_num}: no content stream found.")

        digest = hashlib.sha256(raw_content).hexdigest()
        checksums.append(digest)

    passed = len(issues) == 0
    if passed:
        report = (
            f"OK – {num_pages} page(s) verified. "
            f"All dimensions within tolerance."
        )
    else:
        report = "FAILED – " + " | ".join(issues)

    return {"passed": passed, "report": report, "checksums": checksums}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_content_bytes(page: pypdf.PageObject) -> bytes:
    """Return the raw bytes of a page's content stream(s)."""
    raw = b""
    content = page.get("/Contents")
    if content is None:
        return raw

    # Contents may be a single indirect stream reference or an array of
    # references.  Resolve the object; if it is list-like (ArrayObject is a
    # subclass of list in pypdf), iterate the items; otherwise treat it as a
    # single stream.  Both branches delegate to get_data() which is part of
    # pypdf's public API.
    resolved = content.get_object()
    if isinstance(resolved, list):
        for obj in resolved:
            stream = obj.get_object()
            if hasattr(stream, "get_data"):
                raw += stream.get_data()
    else:
        if hasattr(resolved, "get_data"):
            raw += resolved.get_data()

    return raw
