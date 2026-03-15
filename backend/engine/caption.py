"""
caption.py – Caption block composition for CRC 2.111-compliant pleadings.

Responsibilities
----------------
* Assemble the structured caption block required by CRC 2.111(b):
    - Court name and division
    - Plaintiff(s) vs. Defendant(s)
    - Case number
    - Document title (e.g. "COMPLAINT FOR DAMAGES")
* Return a ``CaptionBlock`` object that records the y-position at which the
  caption ends so ``renderer.py`` can pass that as ``start_position`` to
  ``content.flow_text()``.

CRC 2.111(b) caption requirements enforced here
-------------------------------------------------
* Court name centred or left-aligned in the heading area.
* Party names left-aligned in the left column.
* Case number right-aligned to the right column.
* Document title centred below the party block.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .grid import PageGrid
    from .pos import PagePosition


@dataclass
class CaptionLine:
    """A single rendered line within the caption block."""

    text: str
    x: float
    y: float
    alignment: str = "left"   # "left" | "center" | "right"
    page: int = 1


@dataclass
class CaptionBlock:
    """All rendered lines that make up the caption."""

    lines: list[CaptionLine] = field(default_factory=list)

    @property
    def end_position(self) -> "PagePosition":
        """Return the page position immediately after the last caption line."""
        from .pos import PagePosition

        if not self.lines:
            raise ValueError("CaptionBlock contains no lines.")
        last = self.lines[-1]
        return PagePosition(x=last.x, y=last.y + 24.0, page=last.page)


def _add_line(
    block: CaptionBlock,
    text: str,
    *,
    x: float,
    y: float,
    alignment: str = "left",
    page: int = 1,
) -> float:
    """Append *text* to *block* and return the y-position of the next line."""
    block.lines.append(CaptionLine(text=text, x=x, y=y, alignment=alignment, page=page))
    return y + 24.0  # double-spaced 12 pt = 24 pt advance


def build_caption(
    caption_data: dict[str, Any],
    *,
    grid: "PageGrid",
    origin: "PagePosition",
) -> CaptionBlock:
    """Compose the CRC 2.111(b) caption block.

    Parameters
    ----------
    caption_data:
        Dictionary with the following keys:

        ``court_name`` (str)
            Full name of the court (e.g. "SUPERIOR COURT OF CALIFORNIA,
            COUNTY OF LOS ANGELES").
        ``division`` (str, optional)
            Court division or branch.
        ``plaintiffs`` (list[str])
            Ordered list of plaintiff names.
        ``defendants`` (list[str])
            Ordered list of defendant names.
        ``case_number`` (str)
            Assigned case number.
        ``document_title`` (str)
            Title of the pleading document.

    grid:
        Page geometry from ``grid.build_grid()``.
    origin:
        Top-left starting position for the caption block.

    Returns
    -------
    CaptionBlock
        Immutable caption layout ready for PDF assembly.
    """
    block = CaptionBlock()
    current_y = origin.y
    page = origin.page

    # Court name (centred)
    current_y = _add_line(
        block,
        caption_data.get("court_name", ""),
        x=grid.text_column_left,
        y=current_y,
        alignment="center",
        page=page,
    )

    # Optional division
    if division := caption_data.get("division", "").strip():
        current_y = _add_line(
            block, division, x=grid.text_column_left, y=current_y,
            alignment="center", page=page,
        )

    # Blank separator line
    current_y += 24.0

    # Plaintiffs (left column)
    for name in caption_data.get("plaintiffs", []):
        current_y = _add_line(
            block, name, x=grid.text_column_left, y=current_y, page=page,
        )
    current_y = _add_line(
        block, "Plaintiff(s),", x=grid.text_column_left, y=current_y, page=page,
    )
    current_y = _add_line(
        block, "vs.", x=grid.text_column_left, y=current_y, page=page,
    )

    # Defendants (left column)
    for name in caption_data.get("defendants", []):
        current_y = _add_line(
            block, name, x=grid.text_column_left, y=current_y, page=page,
        )
    current_y = _add_line(
        block, "Defendant(s).", x=grid.text_column_left, y=current_y, page=page,
    )

    # Case number (right-aligned)
    current_y = _add_line(
        block,
        f"Case No.: {caption_data.get('case_number', '')}",
        x=grid.text_column_left,
        y=current_y,
        alignment="right",
        page=page,
    )

    # Blank separator
    current_y += 24.0

    # Document title (centred)
    _add_line(
        block,
        caption_data.get("document_title", ""),
        x=grid.text_column_left,
        y=current_y,
        alignment="center",
        page=page,
    )

    return block
