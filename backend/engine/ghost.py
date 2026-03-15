"""
ghost.py – Ghost Protocol: metadata sanitisation before PDF output.

Responsibilities
----------------
* Strip all document metadata that could identify the drafting system,
  the operator's machine, or any personally identifiable information (PII)
  not intentionally included in the pleading:
    - XMP metadata streams
    - Document Information Dictionary (Author, Creator, Producer, etc.)
    - Embedded file system paths
    - Timestamps that reveal the drafting timeline
* Return sanitised PDF bytes ready to be passed to ``pdfa.enforce_pdfa()``.

Ghost Protocol design rationale
---------------------------------
Legal documents filed with courts are public records.  Metadata embedded
by generic PDF toolchains (author names, software versions, edit history,
etc.) can inadvertently disclose information about the drafting party's
identity, tools, or strategy.  The Ghost Protocol ensures that only the
content explicitly placed in the pleading is present in the output file.

This module is called by ``renderer.py`` immediately before the PDF/A
conformance step.
"""

from __future__ import annotations

# Metadata fields that are PERMITTED to remain in the output document
_ALLOWED_METADATA_KEYS: frozenset[str] = frozenset(
    {
        "Title",        # Document title from the caption
        "Subject",      # Case number / court
        "Keywords",     # Optional – filing party may supply
        "CreationDate", # Required by PDF/A-2b; set to a normalised value
        "ModDate",      # Required by PDF/A-2b; identical to CreationDate
    }
)


class GhostProtocolError(RuntimeError):
    """Raised when metadata sanitisation cannot be completed."""


def sanitise_metadata(pdf_bytes: bytes) -> bytes:
    """Remove all non-permitted metadata from *pdf_bytes*.

    Parameters
    ----------
    pdf_bytes:
        Raw PDF document bytes as produced by the assembly layer.

    Returns
    -------
    bytes
        PDF bytes with all non-permitted metadata stripped.

    Raises
    ------
    GhostProtocolError
        If the sanitisation pass encounters an unrecoverable error.

    Notes
    -----
    The proprietary implementation of this function will be provided when the
    ``ghost.py`` script contents are pasted in.  Until then this placeholder
    raises ``NotImplementedError`` to prevent silent pass-through of
    unsanitised documents.
    """
    raise NotImplementedError(
        "ghost.sanitise_metadata: replace this placeholder with the "
        "proprietary Ghost Protocol implementation."
    )


def strip_xmp(pdf_bytes: bytes) -> bytes:
    """Remove the XMP metadata stream from *pdf_bytes*.

    This is a lower-level helper exposed for testing.  Production code
    should call ``sanitise_metadata()`` instead.
    """
    raise NotImplementedError(
        "ghost.strip_xmp: replace this placeholder with the proprietary "
        "XMP-stripping implementation."
    )


def strip_info_dict(pdf_bytes: bytes) -> bytes:
    """Clear the Document Information Dictionary from *pdf_bytes*.

    This is a lower-level helper exposed for testing.  Production code
    should call ``sanitise_metadata()`` instead.
    """
    raise NotImplementedError(
        "ghost.strip_info_dict: replace this placeholder with the proprietary "
        "info-dict-stripping implementation."
    )
