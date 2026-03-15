"""
renderer.py – Main entry point for the Compass Outlaw legal drafting engine.

``compile_pleading()`` is the sole public API.  It orchestrates the full
render pipeline in the following order:

1. Verify inputs against CRC 2.111 (verify.py)
2. Resolve fonts and typographic metrics (fonts.py)
3. Lay out the absolute geometry grid (grid.py)
4. Compose the caption block (caption.py)
5. Flow body text with word-wrap (content.py)
6. Append exhibit attachments (exhibits.py)
7. Apply redaction overlays where required (redact.py)
8. Strip metadata via Ghost Protocol (ghost.py)
9. Enforce PDF/A-2b conformance (pdfa.py)
10. Return the finalised PDF bytes

CRC 2.111 compliance is enforced at zero tolerance: any violation raised by
``verify.py`` aborts the pipeline immediately.
"""

from __future__ import annotations

from typing import Any

from .caption import build_caption
from .content import flow_text
from .exhibits import attach_exhibits
from .fonts import resolve_fonts
from .ghost import sanitise_metadata
from .grid import build_grid
from .pdfa import enforce_pdfa
from .pos import PagePosition
from .redact import apply_redactions
from .verify import verify_crc_2111


def compile_pleading(
    pleading_data: dict[str, Any],
    *,
    redactions: list[dict[str, Any]] | None = None,
    output_path: str | None = None,
) -> bytes:
    """Compile a CRC 2.111-compliant pleading PDF.

    Parameters
    ----------
    pleading_data:
        Structured pleading content.  Expected keys are documented in
        ``backend/engine/README.md``.
    redactions:
        Optional list of redaction descriptors.  Each entry must contain
        ``page``, ``x``, ``y``, ``width``, and ``height`` keys.
    output_path:
        If supplied the compiled PDF bytes are also written to this path.

    Returns
    -------
    bytes
        The compiled, conformant PDF document.

    Raises
    ------
    CRCViolationError
        If any CRC 2.111 constraint is breached (zero-tolerance).
    """
    # Step 1 – compliance gate (raises CRCViolationError on any violation)
    verify_crc_2111(pleading_data)

    # Step 2 – resolve fonts and typographic metrics
    font_metrics = resolve_fonts(pleading_data.get("font_preferences", {}))

    # Step 3 – build the absolute geometry grid
    grid = build_grid(font_metrics)

    # Step 4 – compose the caption block
    origin = PagePosition(x=grid.left_margin, y=grid.top_margin)
    caption_block = build_caption(pleading_data["caption"], grid=grid, origin=origin)

    # Step 5 – flow body text
    body_blocks = flow_text(
        pleading_data.get("body", ""),
        grid=grid,
        font_metrics=font_metrics,
        start_position=caption_block.end_position,
    )

    # Step 6 – attach exhibits
    exhibit_pages = attach_exhibits(
        pleading_data.get("exhibits", []),
        grid=grid,
        font_metrics=font_metrics,
    )

    # Step 7 – apply redaction overlays
    redaction_list = redactions or []
    redacted_blocks = apply_redactions(body_blocks, redaction_list)

    # Step 8 – strip metadata (Ghost Protocol)
    raw_pdf_bytes = _assemble_pdf(
        caption_block=caption_block,
        body_blocks=redacted_blocks,
        exhibit_pages=exhibit_pages,
        grid=grid,
    )
    sanitised_bytes = sanitise_metadata(raw_pdf_bytes)

    # Step 9 – enforce PDF/A-2b conformance
    conformant_bytes = enforce_pdfa(sanitised_bytes)

    if output_path:
        with open(output_path, "wb") as fh:
            fh.write(conformant_bytes)

    return conformant_bytes


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _assemble_pdf(
    *,
    caption_block: Any,
    body_blocks: list[Any],
    exhibit_pages: list[Any],
    grid: Any,
) -> bytes:
    """Assemble raw PDF bytes from the rendered blocks.

    This is a placeholder for the low-level PDF construction logic that will
    be provided when the proprietary script contents are pasted in.
    """
    raise NotImplementedError(
        "_assemble_pdf: replace this placeholder with the proprietary "
        "PDF-construction implementation."
    )
