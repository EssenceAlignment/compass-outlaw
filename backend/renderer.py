"""
renderer.py – Compile a legal pleading PDF from structured input data.

Produces California-style pleading paper (28 ruled lines, left-margin line
numbers) using ReportLab.  The output is a standard PDF that is subsequently
processed by pdfa.py and verify.py.
"""

import io
import re
import textwrap

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas

# ---------------------------------------------------------------------------
# Public page-geometry constants (also used by verify.py)
# ---------------------------------------------------------------------------
PAGE_WIDTH, PAGE_HEIGHT = letter  # 612 × 792 pt

DEFAULT_GEO = {
    "lines_per_page": 28,
    "margin_top": 1.0,     # inches
    "margin_bottom": 1.0,  # inches
    "margin_left": 1.5,    # inches  (wide for line-number gutter)
    "margin_right": 0.5,   # inches
    "font_size": 12,       # points
}

# Width (in points) of the line-number gutter inside the left margin
_GUTTER_WIDTH = 0.35 * inch
# Horizontal rule width for the double left rule
_RULE_GAP = 3


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _resolve_geo(geo: dict) -> dict:
    """Return a geometry dict that fills any missing keys with defaults."""
    resolved = dict(DEFAULT_GEO)
    resolved.update({k: v for k, v in geo.items() if v is not None})
    return resolved


def _md_to_lines(body_md: str, max_chars: int = 80) -> list[str]:
    """
    Convert a Markdown string to a flat list of plain-text lines.

    Headings are upper-cased and centred with a CENTRE: prefix so the
    renderer knows to centre them.  Blank lines in the source are preserved
    as empty strings so vertical spacing is maintained.
    """
    lines: list[str] = []
    for raw in body_md.splitlines():
        heading = re.match(r'^(?:#{1,6})\s+(.*)', raw)
        if heading:
            text = heading.group(1).strip().upper()
            lines.append(f"CENTRE:{text}")
            continue

        bold_only = re.match(r'^\*\*(.+)\*\*$', raw.strip())
        if bold_only:
            text = bold_only.group(1).strip()
            for sub in textwrap.wrap(text, max_chars) or ['']:
                lines.append(f"BOLD:{sub}")
            continue

        # Strip remaining Markdown emphasis markers
        plain = re.sub(r'\*{1,3}(.+?)\*{1,3}', r'\1', raw)
        plain = re.sub(r'_{1,2}(.+?)_{1,2}', r'\1', plain)
        plain = plain.strip()

        if not plain:
            lines.append('')
            continue

        for sub in textwrap.wrap(plain, max_chars) or [plain]:
            lines.append(sub)

    return lines


def _draw_page_template(
    c: rl_canvas.Canvas,
    identity: dict,
    geo: dict,
    lines_per_page: int,
    margin_top: float,
    margin_bottom: float,
    margin_left: float,
    margin_right: float,
    line_height: float,
    page_number: int,
) -> None:
    """Draw the static pleading-paper template for one page."""
    c.saveState()
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.5)

    text_right = PAGE_WIDTH - margin_right
    text_top = PAGE_HEIGHT - margin_top
    text_bottom = margin_bottom

    # Horizontal ruled lines
    for i in range(lines_per_page):
        y = text_top - (i + 1) * line_height
        c.line(margin_left, y, text_right, y)

    # Double vertical rule on left (pleading paper convention)
    rule_x1 = margin_left - _GUTTER_WIDTH
    rule_x2 = rule_x1 + _RULE_GAP
    c.line(rule_x1, text_top, rule_x1, text_bottom)
    c.line(rule_x2, text_top, rule_x2, text_bottom)

    # Single vertical rule on right
    c.line(text_right, text_top, text_right, text_bottom)

    # Line numbers in the gutter
    c.setFont("Times-Roman", 8)
    for i in range(lines_per_page):
        y = text_top - (i + 0.7) * line_height
        c.drawCentredString(rule_x1 - 6, y, str(i + 1))

    # Case caption header (page 1 only)
    if page_number == 1:
        c.setFont("Times-Roman", 10)
        filer_name = identity.get("filer_name", "")
        filer_address = identity.get("filer_address", "")
        case_number = identity.get("case_number", "")
        court = identity.get("court", "")

        header_lines = [ln for ln in [filer_name, filer_address, court, case_number] if ln]
        y_pos = PAGE_HEIGHT - 0.5 * inch
        for hl in header_lines:
            c.drawString(margin_left, y_pos, hl)
            y_pos -= 12

    # Page number at bottom centre
    c.setFont("Times-Roman", 10)
    c.drawCentredString(PAGE_WIDTH / 2, margin_bottom / 2, str(page_number))

    c.restoreState()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compile_pleading(identity: dict, geo: dict, body_md: str) -> bytes:
    """
    Compile a legal pleading PDF.

    Parameters
    ----------
    identity : dict
        Filer and case information.  Recognised keys:
        ``filer_name``, ``filer_address``, ``case_number``, ``case_title``,
        ``court``.
    geo : dict
        Grid geometry settings.  Keys and defaults match ``DEFAULT_GEO``.
    body_md : str
        Markdown text of the pleading body.

    Returns
    -------
    bytes
        Raw PDF bytes (not yet PDF/A-compliant).
    """
    g = _resolve_geo(geo)

    lines_per_page: int = int(g["lines_per_page"])
    margin_top: float = float(g["margin_top"]) * inch
    margin_bottom: float = float(g["margin_bottom"]) * inch
    margin_left: float = float(g["margin_left"]) * inch
    margin_right: float = float(g["margin_right"]) * inch
    font_size: float = float(g["font_size"])

    content_height = PAGE_HEIGHT - margin_top - margin_bottom
    line_height = content_height / lines_per_page

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)

    # Document-level metadata
    c.setTitle(identity.get("case_title", "Legal Pleading"))
    c.setAuthor(identity.get("filer_name", ""))
    c.setSubject(identity.get("case_number", ""))
    c.setCreator("Compass Outlaw")

    text_lines = _md_to_lines(body_md)
    text_x = margin_left + 0.05 * inch  # slight indent from the left rule
    text_top = PAGE_HEIGHT - margin_top

    page_number = 1
    line_idx = 0
    total_lines = len(text_lines)

    # Always render at least one page
    while True:
        _draw_page_template(
            c, identity, g, lines_per_page,
            margin_top, margin_bottom, margin_left, margin_right,
            line_height, page_number,
        )

        for slot in range(lines_per_page):
            if line_idx >= total_lines:
                break

            raw_line = text_lines[line_idx]
            line_idx += 1

            y = text_top - (slot + 0.72) * line_height

            if raw_line.startswith("CENTRE:"):
                c.setFont("Times-Bold", font_size)
                text = raw_line[len("CENTRE:"):]
                text_right = PAGE_WIDTH - margin_right
                centre_x = (margin_left + text_right) / 2
                c.drawCentredString(centre_x, y, text)
            elif raw_line.startswith("BOLD:"):
                c.setFont("Times-Bold", font_size)
                c.drawString(text_x, y, raw_line[5:])
            elif raw_line == "":
                pass  # blank line – no text drawn
            else:
                c.setFont("Times-Roman", font_size)
                c.drawString(text_x, y, raw_line)

        if line_idx >= total_lines:
            break

        c.showPage()
        page_number += 1

    c.save()
    return buf.getvalue()
