"""
pos.py – Low-level x/y positioning helpers for the pleading layout engine.

Responsibilities
----------------
* Provide the ``PagePosition`` dataclass used across all engine modules to
  communicate the current render cursor position.
* Offer utility functions for common positional calculations (advancing by
  line, moving to a new page, computing centred x-offsets, etc.).
* Act as a dependency-free foundation layer imported by ``grid.py``,
  ``content.py``, ``caption.py``, and ``renderer.py``.

All coordinates are in PDF points (1 pt = 1/72 inch) with the origin at the
top-left corner of the page (positive y increases downward), consistent with
the coordinate system used throughout the Compass Outlaw engine.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass
class PagePosition:
    """A cursor position on a specific page of the document.

    Attributes
    ----------
    x:
        Horizontal position in points from the left edge of the page.
    y:
        Vertical position in points from the top edge of the page.
    page:
        1-indexed page number.
    """

    x: float
    y: float
    page: int = 1

    def advance(self, *, dy: float = 0.0, dx: float = 0.0) -> "PagePosition":
        """Return a new position advanced by *dx* and *dy*."""
        return replace(self, x=self.x + dx, y=self.y + dy)

    def next_line(self, line_spacing: float) -> "PagePosition":
        """Return the position of the next text line."""
        return self.advance(dy=line_spacing)

    def next_page(self, *, top_margin: float, left_margin: float) -> "PagePosition":
        """Return the position at the top of the next page."""
        return PagePosition(x=left_margin, y=top_margin, page=self.page + 1)

    def with_x(self, x: float) -> "PagePosition":
        """Return a copy with a new x-coordinate."""
        return replace(self, x=x)

    def with_y(self, y: float) -> "PagePosition":
        """Return a copy with a new y-coordinate."""
        return replace(self, y=y)

    def __add__(self, other: "PagePosition") -> "PagePosition":
        if self.page != other.page:
            raise ValueError(
                "Cannot add positions on different pages "
                f"({self.page} vs {other.page})."
            )
        return PagePosition(x=self.x + other.x, y=self.y + other.y, page=self.page)


def centre_x(text_width: float, column_left: float, column_right: float) -> float:
    """Return the x-position that centres *text_width* within the column."""
    column_width = column_right - column_left
    return column_left + (column_width - text_width) / 2.0


def right_align_x(text_width: float, column_right: float) -> float:
    """Return the x-position that right-aligns *text_width* to *column_right*."""
    return column_right - text_width


def is_past_bottom_margin(position: PagePosition, page_height: float, bottom_margin: float) -> bool:
    """Return ``True`` if *position* has exceeded the printable area."""
    return position.y > page_height - bottom_margin
