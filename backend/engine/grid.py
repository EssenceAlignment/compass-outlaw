"""
grid.py – Absolute geometry for CRC 2.111-compliant pleading pages.

Responsibilities
----------------
* Define paper dimensions and all fixed margins required by CRC 2.111.
* Compute absolute x/y coordinates for every ruled line (28 lines/page).
* Expose column boundaries (line-number gutter, text column, right margin).
* Provide helper methods used by ``renderer.py``, ``content.py``, and
  ``caption.py`` to place content at precise positions.

CRC 2.111 constraints enforced here
-------------------------------------
* Paper: 8½ × 11 inches.
* Top margin:    1 inch.
* Bottom margin: 1 inch (line 28 must not exceed this boundary).
* Left margin:   1 inch (inside edge of text column, excluding line numbers).
* Right margin:  ½ inch.
* Line spacing:  double-spaced at 12 pt (≈ 24 pt between baselines).
* Line numbers:  1–28, printed in the left gutter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fonts import FontMetrics

# ---------------------------------------------------------------------------
# Constants – all values in points (1 pt = 1/72 inch)
# ---------------------------------------------------------------------------

PAGE_WIDTH_PT: float = 8.5 * 72      # 612 pt
PAGE_HEIGHT_PT: float = 11.0 * 72    # 792 pt

MARGIN_TOP_PT: float = 1.0 * 72      # 72 pt
MARGIN_BOTTOM_PT: float = 1.0 * 72   # 72 pt
MARGIN_LEFT_PT: float = 1.0 * 72     # 72 pt  (text column left edge)
MARGIN_RIGHT_PT: float = 0.5 * 72    # 36 pt

LINE_GUTTER_WIDTH_PT: float = 0.5 * 72   # 36 pt  (line-number column)

LINES_PER_PAGE: int = 28
LINE_SPACING_PT: float = 24.0        # double-spaced 12 pt body text


@dataclass(frozen=True)
class PageGrid:
    """Immutable geometry descriptor for a single pleading page."""

    page_width: float = PAGE_WIDTH_PT
    page_height: float = PAGE_HEIGHT_PT
    top_margin: float = MARGIN_TOP_PT
    bottom_margin: float = MARGIN_BOTTOM_PT
    left_margin: float = MARGIN_LEFT_PT
    right_margin: float = MARGIN_RIGHT_PT
    gutter_width: float = LINE_GUTTER_WIDTH_PT
    lines_per_page: int = LINES_PER_PAGE
    line_spacing: float = LINE_SPACING_PT

    # Derived – populated by __post_init__ via object.__setattr__ (frozen)
    line_y_positions: tuple[float, ...] = field(default_factory=tuple, init=False)
    text_column_width: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        text_col_width = (
            self.page_width
            - self.left_margin
            - self.right_margin
            - self.gutter_width
        )
        object.__setattr__(self, "text_column_width", text_col_width)

        positions = tuple(
            self.top_margin + i * self.line_spacing
            for i in range(self.lines_per_page)
        )
        object.__setattr__(self, "line_y_positions", positions)

    @property
    def text_column_left(self) -> float:
        """Left edge of the text column (right of the line-number gutter)."""
        return self.left_margin + self.gutter_width

    @property
    def text_column_right(self) -> float:
        """Right edge of the text column."""
        return self.page_width - self.right_margin

    def line_y(self, line_number: int) -> float:
        """Return the baseline y-position for a 1-indexed line number (1–28)."""
        if not 1 <= line_number <= self.lines_per_page:
            raise ValueError(
                f"line_number must be 1–{self.lines_per_page}, got {line_number}"
            )
        return self.line_y_positions[line_number - 1]

    def gutter_x(self) -> float:
        """Return the x-position for printing the line number in the gutter."""
        return self.left_margin  # right-aligned to gutter edge


def build_grid(font_metrics: "FontMetrics | None" = None) -> PageGrid:
    """Construct and return the canonical CRC 2.111 page grid.

    Parameters
    ----------
    font_metrics:
        Reserved for future use – allows grid adjustments based on the
        resolved font (e.g. slightly different line spacing for condensed
        typefaces).  Currently unused; pass ``None``.

    Returns
    -------
    PageGrid
        Immutable geometry descriptor ready for use by the render pipeline.
    """
    return PageGrid()
