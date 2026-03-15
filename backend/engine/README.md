# Compass Outlaw – Backend Engine

California Rule of Court (CRC) 2.111 zero-tolerance legal drafting engine.

## Module overview

| Module | Responsibility |
|---|---|
| `renderer.py` | **Main entry point.** `compile_pleading()` orchestrates the full pipeline. |
| `grid.py` | Absolute geometry: paper dimensions, margins, 28-line grid, column boundaries. |
| `content.py` | Word-wrapping and text-flow for pleading body text. |
| `caption.py` | CRC 2.111(b) caption block: court, parties, case number, document title. |
| `exhibits.py` | Exhibit attachment management and sequential labelling (A, B, C…). |
| `fonts.py` | Font validation, registration, and typographic metrics. |
| `ghost.py` | **Ghost Protocol** – strips all non-permitted metadata before output. |
| `pdfa.py` | PDF/A-2b conformance layer (ISO 19005-2). |
| `pos.py` | Low-level `PagePosition` dataclass and x/y positioning helpers. |
| `redact.py` | Redaction overlay: positional and keyword-based text removal. |
| `verify.py` | CRC 2.111 compliance gate – zero-tolerance enforcement at pipeline entry. |

## Render pipeline

```
compile_pleading(pleading_data)
        │
        ├─ 1. verify.verify_crc_2111()         ← zero-tolerance compliance gate
        ├─ 2. fonts.resolve_fonts()             ← validate & resolve typography
        ├─ 3. grid.build_grid()                 ← compute absolute page geometry
        ├─ 4. caption.build_caption()           ← lay out CRC 2.111(b) caption
        ├─ 5. content.flow_text()               ← word-wrap body text
        ├─ 6. exhibits.attach_exhibits()        ← append exhibit separator pages
        ├─ 7. redact.apply_redactions()         ← apply redaction overlays
        ├─ 8. _assemble_pdf()                   ← low-level PDF construction
        ├─ 9. ghost.sanitise_metadata()         ← Ghost Protocol metadata strip
        └─ 10. pdfa.enforce_pdfa()              ← PDF/A-2b conformance
```

## Public API

```python
from backend.engine import compile_pleading

pdf_bytes = compile_pleading(
    pleading_data={
        "caption": {
            "court_name": "SUPERIOR COURT OF CALIFORNIA, COUNTY OF LOS ANGELES",
            "division": "CENTRAL DISTRICT",
            "plaintiffs": ["JANE DOE"],
            "defendants": ["JOHN DOE"],
            "case_number": "23STCV00001",
            "document_title": "COMPLAINT FOR DAMAGES",
        },
        "body": "Plaintiff alleges as follows: ...",
        "exhibits": [
            {"description": "Contract dated January 1, 2023", "source_path": "/path/to/contract.pdf"},
        ],
        "signature": "Jane Doe, Pro Per",
        "date": "March 15, 2026",
        "font_preferences": {
            "family": "Times New Roman",
            "size_pt": 12,
        },
    },
    redactions=[
        # Redact by keyword
        {"keyword": "sensitive term"},
        # Redact by position (page 1, points from top-left)
        {"page": 1, "x": 100, "y": 200, "width": 150, "height": 20},
    ],
    output_path="output/complaint.pdf",
)
```

## `pleading_data` schema

| Key | Type | Required | Description |
|---|---|---|---|
| `caption` | `dict` | ✅ | See caption sub-keys below. |
| `body` | `str` | – | Pleading body text; paragraphs separated by blank lines. |
| `exhibits` | `list[dict]` | – | List of exhibit descriptors (`description`, `source_path`). |
| `signature` | `str` | ✅ | Signature block text (CRC 2.111(f)). |
| `date` | `str` | ✅ | Date line adjacent to signature (CRC 2.111(g)). |
| `font_preferences` | `dict` | – | `family` and `size_pt` overrides (default: Times New Roman 12 pt). |

### Caption sub-keys

| Key | Type | Required | CRC rule |
|---|---|---|---|
| `court_name` | `str` | ✅ | 2.111(b) |
| `division` | `str` | – | 2.111(b) |
| `plaintiffs` | `list[str]` | ✅ | 2.111(b) |
| `defendants` | `list[str]` | ✅ | 2.111(b) |
| `case_number` | `str` | ✅ | 2.111(b) |
| `document_title` | `str` | ✅ | 2.111(b) |

## CRC 2.111 constraints

All output documents are validated against the following rules before being
returned.  Any violation raises `CRCViolationError` and **no** PDF is produced.

| Rule | Requirement |
|---|---|
| 2.111(a)(1) | Paper size: 8½ × 11 inches |
| 2.111(a)(2) | Roman typeface, 12 pt minimum |
| 2.111(a)(3) | Line numbers 1–28 on each page |
| 2.111(a)(4) | Double-spaced body text |
| 2.111(a)(5) | Margins: 1″ top/bottom, 1″ left, ½″ right |
| 2.111(b) | Complete caption block |
| 2.111(c) | Consecutive Arabic page numbers, bottom-centred |
| 2.111(f) | Signature block on final page |
| 2.111(g) | Date line adjacent to signature |
| 2.111(h) | Exhibits labelled with consecutive capital letters |

## Scaffolding note

The files in this directory are **scaffolded placeholders**.  Functions that
require the proprietary implementation raise `NotImplementedError` with an
explanatory message.  Paste the corresponding proprietary script contents into
each file to complete the implementation.  The module interfaces, docstrings,
type hints, and pipeline wiring are ready to receive those implementations
without further structural changes.
