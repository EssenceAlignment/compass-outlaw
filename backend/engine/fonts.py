"""
fonts.py – Font registration, size normalisation, and CRC typographic metrics.

Responsibilities
----------------
* Register and validate the fonts permitted by CRC 2.111(a)(2):
    - Times New Roman (preferred)
    - Courier New
    - Arial / Helvetica (fallback)
* Provide a ``FontMetrics`` object consumed by ``grid.py``, ``content.py``,
  and ``caption.py`` for accurate text-width measurement.
* Enforce the 12-point minimum type size required by CRC 2.111(a)(2).
* Expose ``resolve_fonts()`` as the sole public API called by ``renderer.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# ---------------------------------------------------------------------------
# CRC 2.111 font constraints
# ---------------------------------------------------------------------------

MIN_FONT_SIZE_PT: float = 12.0
DEFAULT_FONT_FAMILY: str = "Times New Roman"
DEFAULT_FONT_SIZE_PT: float = 12.0

PERMITTED_FONTS: frozenset[str] = frozenset(
    {
        "Times New Roman",
        "Times",
        "Courier New",
        "Courier",
        "Arial",
        "Helvetica",
    }
)

# Approximate average character widths (in points) at 12 pt for common fonts.
# Replace with precise AFM data when the proprietary font module is pasted in.
_AVG_CHAR_WIDTH_PT: dict[str, float] = {
    "Times New Roman": 6.0,
    "Times": 6.0,
    "Courier New": 7.2,
    "Courier": 7.2,
    "Arial": 6.6,
    "Helvetica": 6.6,
}


@dataclass(frozen=True)
class FontMetrics:
    """Resolved typographic metrics for a single font/size combination."""

    family: str
    size_pt: float
    avg_char_width_pt: float
    line_height_pt: float   # typically size_pt * 2 for double-spacing
    is_bold: bool = False
    is_italic: bool = False


class CRCFontError(ValueError):
    """Raised when a requested font or size violates CRC 2.111 constraints."""


def resolve_fonts(preferences: dict[str, Any]) -> FontMetrics:
    """Resolve font preferences into a validated ``FontMetrics`` object.

    Parameters
    ----------
    preferences:
        Optional font override dictionary.  Recognised keys:

        ``family`` (str)
            Font family name.  Must be in ``PERMITTED_FONTS``.
        ``size_pt`` (float)
            Font size in points.  Must be ≥ ``MIN_FONT_SIZE_PT`` (12 pt).
        ``bold`` (bool, optional)
        ``italic`` (bool, optional)

    Returns
    -------
    FontMetrics
        Validated typographic metrics ready for use in the render pipeline.

    Raises
    ------
    CRCFontError
        If the requested font or size violates CRC 2.111 constraints.
    """
    family = preferences.get("family", DEFAULT_FONT_FAMILY)
    size_pt = float(preferences.get("size_pt", DEFAULT_FONT_SIZE_PT))

    if family not in PERMITTED_FONTS:
        raise CRCFontError(
            f"Font '{family}' is not permitted by CRC 2.111(a)(2). "
            f"Permitted fonts: {sorted(PERMITTED_FONTS)}"
        )

    if size_pt < MIN_FONT_SIZE_PT:
        raise CRCFontError(
            f"Font size {size_pt} pt is below the CRC 2.111(a)(2) minimum "
            f"of {MIN_FONT_SIZE_PT} pt."
        )

    avg_char_width = _AVG_CHAR_WIDTH_PT.get(family, 6.0) * (size_pt / 12.0)

    return FontMetrics(
        family=family,
        size_pt=size_pt,
        avg_char_width_pt=avg_char_width,
        line_height_pt=size_pt * 2.0,   # double-spacing
        is_bold=bool(preferences.get("bold", False)),
        is_italic=bool(preferences.get("italic", False)),
    )
