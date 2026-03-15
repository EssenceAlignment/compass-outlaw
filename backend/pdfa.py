"""
pdfa.py – Apply PDF/A-2b conformance and metadata sanitisation to a PDF.

PDF/A-2b requires:
  • All fonts embedded.
  • An XMP metadata stream declaring the PDF/A conformance identifier.
  • No encryption.
  • Document information dictionary stripped of implementation-specific
    fields that could leak environment data.

This module uses pikepdf to post-process the PDF produced by renderer.py.
"""

import io
from datetime import datetime, timezone

import pikepdf

# ---------------------------------------------------------------------------
# XMP template (PDF/A-2b conformance declaration)
# ---------------------------------------------------------------------------

_XMP_TEMPLATE = """\
<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">

    <rdf:Description rdf:about=""
        xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
      <pdfaid:part>2</pdfaid:part>
      <pdfaid:conformance>B</pdfaid:conformance>
    </rdf:Description>

    <rdf:Description rdf:about=""
        xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:format>application/pdf</dc:format>
      <dc:title>
        <rdf:Alt>
          <rdf:li xml:lang="x-default">{title}</rdf:li>
        </rdf:Alt>
      </dc:title>
      <dc:creator>
        <rdf:Seq>
          <rdf:li>{author}</rdf:li>
        </rdf:Seq>
      </dc:creator>
    </rdf:Description>

    <rdf:Description rdf:about=""
        xmlns:xmp="http://ns.adobe.com/xap/1.0/">
      <xmp:CreatorTool>Compass Outlaw</xmp:CreatorTool>
      <xmp:CreateDate>{create_date}</xmp:CreateDate>
      <xmp:ModifyDate>{modify_date}</xmp:ModifyDate>
    </rdf:Description>

    <rdf:Description rdf:about=""
        xmlns:pdf="http://ns.adobe.com/pdf/1.3/">
      <pdf:Producer>Compass Outlaw / pikepdf</pdf:Producer>
    </rdf:Description>

  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""

# Fields in the document information dictionary that must be removed to
# prevent leaking system / environment metadata.
_DISALLOWED_INFO_KEYS = {"Creator", "Producer", "Keywords", "Trapped"}


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def _xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def apply_pdfa(pdf_bytes: bytes) -> bytes:
    """
    Post-process *pdf_bytes* to produce a PDF/A-2b–compliant document.

    Steps performed:
    1. Open the PDF in memory with pikepdf.
    2. Sanitise the document information dictionary (strip implementation
       metadata, keep only Title / Author / Subject).
    3. Inject an XMP metadata stream that declares PDF/A-2b conformance.
    4. Write the result back to an in-memory buffer and return the bytes.

    Parameters
    ----------
    pdf_bytes : bytes
        Raw PDF bytes as produced by ``renderer.compile_pleading``.

    Returns
    -------
    bytes
        PDF/A-2b–compliant PDF bytes.
    """
    with pikepdf.open(io.BytesIO(pdf_bytes)) as pdf:
        # ---- 1. Sanitise document information dictionary ----------------
        info = pdf.docinfo
        title = str(info.get("/Title", "")) if "/Title" in info else ""
        author = str(info.get("/Author", "")) if "/Author" in info else ""
        subject = str(info.get("/Subject", "")) if "/Subject" in info else ""

        # Remove disallowed / system keys
        for key in list(info.keys()):
            bare = key.lstrip("/")
            if bare in _DISALLOWED_INFO_KEYS:
                del info[key]

        # Ensure required keys are set
        now_pdf = pikepdf.String(datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%S+00'00'"))
        info["/Title"] = pikepdf.String(title)
        info["/Author"] = pikepdf.String(author)
        info["/Subject"] = pikepdf.String(subject)
        info["/CreationDate"] = now_pdf
        info["/ModDate"] = now_pdf

        # ---- 2. Inject XMP metadata -------------------------------------
        iso_now = _iso_now()
        xmp_str = _XMP_TEMPLATE.format(
            title=_xml_escape(title),
            author=_xml_escape(author),
            create_date=iso_now,
            modify_date=iso_now,
        )
        xmp_bytes = xmp_str.encode("utf-8")

        xmp_stream = pdf.make_stream(
            xmp_bytes,
            {
                "/Type": pikepdf.Name("/Metadata"),
                "/Subtype": pikepdf.Name("/XML"),
            },
        )
        pdf.Root["/Metadata"] = xmp_stream

        # ---- 3. Serialise -----------------------------------------------
        out = io.BytesIO()
        pdf.save(out)
        return out.getvalue()
