"""
Compass Outlaw Legal Drafting Engine
=====================================
California Rule of Court (CRC) 2.111 zero-tolerance compliance engine.

Module architecture
-------------------
renderer   Main entry point – ``compile_pleading()`` orchestrates all modules.
grid       Absolute geometry: margins, line positions, column boundaries.
content    Word-wrapping and text-flow logic.
caption    Caption block composition (case number, court, parties).
exhibits   Exhibit attachment management and labelling.
fonts      Font registration, size normalisation, and CRC metrics.
ghost      Ghost Protocol – metadata sanitisation before output.
pdfa       PDF/A-2b conformance layer.
pos        Low-level x/y positioning helpers.
redact     Redaction overlay generation.
verify     CRC 2.111 compliance checks and zero-tolerance enforcement.
"""

from .renderer import compile_pleading

__all__ = ["compile_pleading"]
