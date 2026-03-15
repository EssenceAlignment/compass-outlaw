"""
content.py – Word-wrapping and text-flow logic for pleading body text.

Responsibilities
----------------
* Accept raw body text and break it into lines that fit within the text
  column defined by ``grid.py``.
* Respect CRC 2.111 double-spacing (every rendered line occupies one ruled
  line slot; content wraps to the next slot when a line would overflow).
* Return ordered ``TextBlock`` objects that ``renderer.py`` can hand directly
  to the PDF assembly layer.
* Handle paragraph breaks, indentation, and page-overflow continuation.

This module is called exclusively by ``renderer.py`` after the caption block
has been laid out, so it receives the ``start_position`` at which body text
should begin.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .fonts import FontMetrics
    from .grid import PageGrid
    from .pos import PagePosition


@dataclass
class TextLine:
    """A single rendered line of body text."""

    text: str
    x: float
    y: float
    page: int = 1


@dataclass
class TextBlock:
    """A collection of ``TextLine`` objects that form a logical paragraph."""

    lines: list[TextLine] = field(default_factory=list)

    @property
    def end_position(self) -> "PagePosition":
        """Return the position immediately after the last rendered line."""
        from .pos import PagePosition

        if not self.lines:
            raise ValueError("TextBlock contains no lines.")
        last = self.lines[-1]
        return PagePosition(x=last.x, y=last.y, page=last.page)


def _measure_text(text: str, font_metrics: "FontMetrics") -> float:
    """Return the rendered width of *text* in points.

    Placeholder – replace with actual font-metric measurement once
    ``fonts.py`` is fully implemented.
    """
    return len(text) * font_metrics.avg_char_width_pt


def _wrap_paragraph(
    paragraph: str,
    *,
    max_width: float,
    font_metrics: "FontMetrics",
) -> list[str]:
    """Wrap *paragraph* into a list of lines that each fit within *max_width*.

    Uses a greedy word-wrapping algorithm compatible with CRC 2.111's
    proportional-font requirements.
    """
    words = paragraph.split()
    if not words:
        return [""]

    lines: list[str] = []
    current: list[str] = []
    current_width = 0.0

    for word in words:
        word_width = _measure_text(word + " ", font_metrics)
        if current and current_width + word_width > max_width:
            lines.append(" ".join(current))
            current = [word]
            current_width = word_width
        else:
            current.append(word)
            current_width += word_width

    if current:
        lines.append(" ".join(current))

    return lines


def flow_text(
    body: str,
    *,
    grid: "PageGrid",
    font_metrics: "FontMetrics",
    start_position: "PagePosition",
) -> list[TextBlock]:
    """Flow *body* text into ``TextBlock`` objects within the page grid.

    Parameters
    ----------
    body:
        Raw body text.  Paragraphs are separated by one or more blank lines.
    grid:
        Page geometry from ``grid.build_grid()``.
    font_metrics:
        Resolved font metrics from ``fonts.resolve_fonts()``.
    start_position:
        The page position immediately after the caption block.

    Returns
    -------
    list[TextBlock]
        Ordered list of text blocks ready for PDF assembly.
    """
    paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()]

    blocks: list[TextBlock] = []
    current_y = start_position.y
    current_page = start_position.page

    for para in paragraphs:
        wrapped_lines = _wrap_paragraph(
            para,
            max_width=grid.text_column_width,
            font_metrics=font_metrics,
        )
        block = TextBlock()
        for line_text in wrapped_lines:
            # Overflow to next page when past the bottom margin
            if current_y + grid.line_spacing > grid.page_height - grid.bottom_margin:
                current_page += 1
                current_y = grid.top_margin

            block.lines.append(
                TextLine(
                    text=line_text,
                    x=grid.text_column_left,
                    y=current_y,
                    page=current_page,
                )
            )
            current_y += grid.line_spacing

        blocks.append(block)
        # Extra spacing after paragraph (still counts as one ruled line)
        current_y += grid.line_spacing

    return blocks
