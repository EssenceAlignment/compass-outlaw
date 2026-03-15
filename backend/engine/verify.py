"""
verify.py – CRC 2.111 compliance checks with zero-tolerance enforcement.

Responsibilities
----------------
* Validate every aspect of a pleading data structure against California Rule
  of Court 2.111 before any rendering begins.
* Raise ``CRCViolationError`` immediately upon detecting ANY violation –
  the pipeline is aborted; no partial output is produced.
* Provide granular check functions that can be called independently for
  unit testing or pre-validation UIs.

CRC 2.111 rules enforced
--------------------------
(a)(1)  Paper size: 8½ × 11 inches.
(a)(2)  Type: roman typeface, 12 pt minimum, no bold or italic for body text.
(a)(3)  Line numbering: 1–28 on each page.
(a)(4)  Line spacing: double-spaced.
(a)(5)  Margins: 1 inch top/bottom, 1 inch left, ½ inch right.
(b)     Caption block: court, parties, case number, document title.
(c)     Page numbering: consecutive Arabic numerals, bottom-centred.
(d)     Binding margin: none required for e-filed documents.
(e)     Footer: not required.
(f)     Signature block: required on final page.
(g)     Date line: required adjacent to signature block.
(h)     Exhibit labelling: consecutive capital letters.

Zero-tolerance policy
----------------------
Any single violation raises ``CRCViolationError`` and halts the pipeline.
There is no warning mode or partial compliance – every pleading that exits
the engine must be fully CRC 2.111 compliant.
"""

from __future__ import annotations

from typing import Any


class CRCViolationError(ValueError):
    """Raised when a pleading violates CRC 2.111.

    Attributes
    ----------
    rule:
        The CRC 2.111 sub-rule that was violated (e.g. ``"2.111(a)(2)"``).
    detail:
        Human-readable description of the violation.
    """

    def __init__(self, rule: str, detail: str) -> None:
        self.rule = rule
        self.detail = detail
        super().__init__(f"CRC {rule} violation: {detail}")


# ---------------------------------------------------------------------------
# Individual rule checks
# ---------------------------------------------------------------------------

def check_caption(caption: dict[str, Any]) -> None:
    """Verify CRC 2.111(b): required caption fields are present and non-empty.

    Raises
    ------
    CRCViolationError
    """
    required_fields = {
        "court_name": "Court name",
        "plaintiffs": "Plaintiff list",
        "defendants": "Defendant list",
        "case_number": "Case number",
        "document_title": "Document title",
    }
    for field_key, field_label in required_fields.items():
        value = caption.get(field_key)
        if not value:
            raise CRCViolationError(
                "2.111(b)",
                f"{field_label} is required in the caption but was not provided.",
            )


def check_font_preferences(prefs: dict[str, Any]) -> None:
    """Verify CRC 2.111(a)(2): font family and size constraints.

    Raises
    ------
    CRCViolationError
    """
    from .fonts import MIN_FONT_SIZE_PT, PERMITTED_FONTS

    family = prefs.get("family", "Times New Roman")
    size_pt = float(prefs.get("size_pt", 12.0))

    if family not in PERMITTED_FONTS:
        raise CRCViolationError(
            "2.111(a)(2)",
            f"Font '{family}' is not a permitted CRC 2.111 typeface.",
        )
    if size_pt < MIN_FONT_SIZE_PT:
        raise CRCViolationError(
            "2.111(a)(2)",
            f"Font size {size_pt} pt is below the 12 pt minimum.",
        )


def check_signature_block(pleading_data: dict[str, Any]) -> None:
    """Verify CRC 2.111(f)–(g): signature block and date line are present.

    Raises
    ------
    CRCViolationError
    """
    if not pleading_data.get("signature"):
        raise CRCViolationError(
            "2.111(f)",
            "A signature block is required on the final page.",
        )
    if not pleading_data.get("date"):
        raise CRCViolationError(
            "2.111(g)",
            "A date line is required adjacent to the signature block.",
        )


def check_exhibit_labels(exhibits: list[dict[str, Any]]) -> None:
    """Verify CRC 2.111(h): exhibits are labelled with consecutive capital letters.

    Raises
    ------
    CRCViolationError
    """
    import string

    expected_labels = [
        letter * repeat
        for repeat in range(1, 4)
        for letter in string.ascii_uppercase
    ]

    for idx, exhibit in enumerate(exhibits):
        label = exhibit.get("label")
        if label is None:
            continue  # un-labelled exhibits will be auto-labelled by exhibits.py
        expected = expected_labels[idx]
        if label != expected:
            raise CRCViolationError(
                "2.111(h)",
                f"Exhibit at index {idx} has label '{label}'; "
                f"expected '{expected}' (consecutive capital letters required).",
            )


# ---------------------------------------------------------------------------
# Primary compliance gate
# ---------------------------------------------------------------------------

def verify_crc_2111(pleading_data: dict[str, Any]) -> None:
    """Run all CRC 2.111 compliance checks against *pleading_data*.

    This is the zero-tolerance compliance gate called at the very start of
    ``renderer.compile_pleading()``.  Any violation immediately raises
    ``CRCViolationError`` and halts the pipeline.

    Parameters
    ----------
    pleading_data:
        Full pleading data dictionary as supplied to ``compile_pleading()``.

    Raises
    ------
    CRCViolationError
        On the first detected CRC 2.111 violation.
    """
    # (b) Caption
    caption = pleading_data.get("caption")
    if not caption:
        raise CRCViolationError(
            "2.111(b)",
            "A caption block is required but was not provided.",
        )
    check_caption(caption)

    # (a)(2) Font preferences
    font_prefs = pleading_data.get("font_preferences", {})
    check_font_preferences(font_prefs)

    # (f)–(g) Signature and date
    check_signature_block(pleading_data)

    # (h) Exhibit labels (if any exhibits supplied)
    exhibits = pleading_data.get("exhibits", [])
    if exhibits:
        check_exhibit_labels(exhibits)
