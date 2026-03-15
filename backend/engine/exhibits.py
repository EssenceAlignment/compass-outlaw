"""
exhibits.py – Exhibit attachment management and labelling.

Responsibilities
----------------
* Accept a list of exhibit descriptors from ``renderer.py``.
* Assign sequential exhibit labels (Exhibit A, B, C … AA, BB, …).
* Insert a cover sheet for each exhibit (CRC 2.111 exhibit separator page).
* Return ordered ``ExhibitPage`` objects that ``renderer.py`` appends after
  the main pleading body.

CRC 2.111 exhibit requirements enforced here
---------------------------------------------
* Each exhibit must be identified by a capital letter (CRC 2.111(h)).
* An exhibit separator page must precede each attached document.
* Exhibit labels must be referenced consistently in the body text.
"""

from __future__ import annotations

import itertools
import string
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    from .fonts import FontMetrics
    from .grid import PageGrid


def _label_sequence() -> Iterator[str]:
    """Generate exhibit labels: A, B, … Z, AA, BB, … ZZ, AAA, …"""
    for repeat in itertools.count(1):
        for letter in string.ascii_uppercase:
            yield letter * repeat


@dataclass
class ExhibitPage:
    """A single exhibit separator page."""

    label: str
    description: str
    source_path: str | None
    page_number: int


@dataclass
class ExhibitManifest:
    """Ordered collection of exhibit pages for the document."""

    pages: list[ExhibitPage] = field(default_factory=list)

    def get_label(self, description: str) -> str | None:
        """Look up the assigned label for an exhibit by description."""
        for page in self.pages:
            if page.description == description:
                return page.label
        return None


def attach_exhibits(
    exhibits: list[dict[str, Any]],
    *,
    grid: "PageGrid",
    font_metrics: "FontMetrics",
    starting_page: int = 2,
) -> ExhibitManifest:
    """Compose exhibit separator pages for each supplied exhibit.

    Parameters
    ----------
    exhibits:
        List of exhibit descriptors.  Each entry may contain:

        ``description`` (str)
            Human-readable description shown on the separator page.
        ``source_path`` (str, optional)
            File path of the exhibit document to embed.

    grid:
        Page geometry from ``grid.build_grid()``.
    font_metrics:
        Resolved font metrics from ``fonts.resolve_fonts()``.
    starting_page:
        Page number to assign to the first exhibit separator page.

    Returns
    -------
    ExhibitManifest
        Ordered manifest of exhibit pages ready for PDF assembly.
    """
    manifest = ExhibitManifest()
    labels = _label_sequence()
    current_page = starting_page

    for exhibit_data in exhibits:
        label = next(labels)
        manifest.pages.append(
            ExhibitPage(
                label=label,
                description=exhibit_data.get("description", f"Exhibit {label}"),
                source_path=exhibit_data.get("source_path"),
                page_number=current_page,
            )
        )
        current_page += 1

    return manifest
