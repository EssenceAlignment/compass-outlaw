"""
redact.py – Redaction overlay generation.

Responsibilities
----------------
* Accept a list of ``TextBlock`` objects (from ``content.flow_text()``) and a
  list of redaction descriptors, and produce a new set of blocks where the
  specified regions are replaced with black rectangles.
* Support both positional redactions (page / x / y / width / height) and
  keyword-based redactions (replace all occurrences of a term on a given page).
* Ensure redacted content cannot be recovered from the PDF structure (the
  underlying text is removed, not merely covered by an opaque layer).

Usage in the pipeline
----------------------
``renderer.compile_pleading()`` calls this module after ``content.flow_text()``
and before ``ghost.sanitise_metadata()``.  Redactions are therefore applied to
the logical text layer before PDF assembly, not as a post-processing overlay.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .content import TextBlock


REDACTION_PLACEHOLDER: str = "█"   # visible indicator that text was redacted


@dataclass
class RedactionDescriptor:
    """Describes a single region or keyword to redact.

    Positional redaction
    ---------------------
    Provide ``page``, ``x``, ``y``, ``width``, ``height``.

    Keyword redaction
    ------------------
    Provide ``keyword`` (and optionally ``page`` to limit scope).
    """

    page: int | None = None
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None
    keyword: str | None = None

    @property
    def is_positional(self) -> bool:
        return all(v is not None for v in (self.x, self.y, self.width, self.height))

    @property
    def is_keyword(self) -> bool:
        return self.keyword is not None


def _parse_descriptor(raw: dict[str, Any]) -> RedactionDescriptor:
    return RedactionDescriptor(
        page=raw.get("page"),
        x=raw.get("x"),
        y=raw.get("y"),
        width=raw.get("width"),
        height=raw.get("height"),
        keyword=raw.get("keyword"),
    )


def _line_intersects(line_x: float, line_y: float, desc: RedactionDescriptor) -> bool:
    """Return True if the given line position falls within a positional redaction."""
    if not desc.is_positional:
        return False
    if desc.page is not None and desc.page != 0:  # 0 = all pages
        return False  # page check is done by the caller
    assert desc.x is not None and desc.y is not None
    assert desc.width is not None and desc.height is not None
    return (
        desc.x <= line_x <= desc.x + desc.width
        and desc.y <= line_y <= desc.y + desc.height
    )


def apply_redactions(
    blocks: "list[TextBlock]",
    redaction_list: list[dict[str, Any]],
) -> "list[TextBlock]":
    """Apply redactions to *blocks* and return the modified list.

    Parameters
    ----------
    blocks:
        Ordered list of ``TextBlock`` objects from ``content.flow_text()``.
    redaction_list:
        List of raw redaction descriptor dicts.  Each entry may contain:

        Positional keys: ``page``, ``x``, ``y``, ``width``, ``height``
        Keyword key:     ``keyword`` (plus optional ``page``)

    Returns
    -------
    list[TextBlock]
        Blocks with redacted content replaced by ``REDACTION_PLACEHOLDER``
        characters.  The underlying text data is fully removed.
    """
    if not redaction_list:
        return blocks

    descriptors = [_parse_descriptor(r) for r in redaction_list]

    for block in blocks:
        for line in block.lines:
            for desc in descriptors:
                # Skip if the descriptor targets a specific page that differs
                if desc.page is not None and desc.page != line.page:
                    continue

                if desc.is_keyword and desc.keyword:
                    if desc.keyword in line.text:
                        line.text = line.text.replace(
                            desc.keyword,
                            REDACTION_PLACEHOLDER * len(desc.keyword),
                        )

                elif desc.is_positional and _line_intersects(line.x, line.y, desc):
                    line.text = REDACTION_PLACEHOLDER * len(line.text)

    return blocks
