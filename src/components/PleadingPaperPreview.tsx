/**
 * PleadingPaperPreview
 *
 * Renders a print-accurate preview of a California pleading paper that
 * conforms to CRC 2.111:
 *   • Page size:  8.5 × 11 in  →  816 × 1056 px at 96 dpi
 *   • Margins:    1 in top/left/bottom, 0.5 in right  →  96/96/96/48 px
 *   • Font:       Times New Roman, 12 pt  →  16 px at 96 dpi
 *   • Line height: 24 pt  →  32 px (line-height: 2 × 16 px)
 *
 * When a PDF Blob is supplied the component embeds it in an <iframe> so the
 * user can visually verify the rendered margins and line spacing.
 */

import { useEffect, useMemo } from 'react';

export interface PleadingPaperPreviewProps {
  /** PDF Blob returned by the backend.  Null = show placeholder. */
  pdfBlob: Blob | null;
  /** Show a loading overlay while the PDF is being generated. */
  isLoading?: boolean;
  /** Optional error message to display instead of content. */
  error?: string | null;
}

/** Width/height constants (pixels at 96 dpi). */
const PAGE_W_PX = 816;
const PAGE_H_PX = 1056;

/** CRC 2.111 margin constants (px). */
const MARGIN_TOP_PX = 96;    // 1 in
const MARGIN_RIGHT_PX = 48;  // 0.5 in
const MARGIN_BOTTOM_PX = 96; // 1 in
const MARGIN_LEFT_PX = 96;   // 1 in

/** Typography constants. */
const FONT_SIZE_PX = 16;     // 12 pt at 96 dpi
const LINE_HEIGHT = 2;       // 2 × 16 px = 32 px ≈ 24 pt at 96 dpi

const pageStyle: React.CSSProperties = {
  position: 'relative',
  width: `${PAGE_W_PX}px`,
  height: `${PAGE_H_PX}px`,
  background: '#ffffff',
  boxShadow: '0 4px 24px rgba(0,0,0,0.18)',
  boxSizing: 'border-box',
  flexShrink: 0,
};

const contentStyle: React.CSSProperties = {
  position: 'absolute',
  inset: 0,
  paddingTop: `${MARGIN_TOP_PX}px`,
  paddingRight: `${MARGIN_RIGHT_PX}px`,
  paddingBottom: `${MARGIN_BOTTOM_PX}px`,
  paddingLeft: `${MARGIN_LEFT_PX}px`,
  fontFamily: "'Times New Roman', Times, serif",
  fontSize: `${FONT_SIZE_PX}px`,
  lineHeight: LINE_HEIGHT,
  boxSizing: 'border-box',
  color: '#1a1a1a',
};

const overlayStyle: React.CSSProperties = {
  position: 'absolute',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: 'rgba(255,255,255,0.85)',
  fontFamily: "'Times New Roman', Times, serif",
  fontSize: '16px',
};

export function PleadingPaperPreview({
  pdfBlob,
  isLoading = false,
  error = null,
}: PleadingPaperPreviewProps) {
  // Create the object URL during the memoization phase (not inside an effect)
  // so we never call setState from within an effect body.
  const objectUrl = useMemo<string | null>(() => {
    if (!pdfBlob) return null;
    return URL.createObjectURL(pdfBlob);
  }, [pdfBlob]);

  // Revoke the URL when it changes (i.e. a new blob arrives) or on unmount,
  // keeping the browser's blob store free of stale references.
  useEffect(() => {
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [objectUrl]);

  return (
    <div style={pageStyle} aria-label="Pleading paper preview">
      {/* PDF iframe — shown when the backend has returned a PDF blob */}
      {objectUrl && !isLoading && !error && (
        <iframe
          src={objectUrl}
          title="Generated pleading PDF"
          style={{ width: '100%', height: '100%', border: 'none' }}
        />
      )}

      {/* Placeholder — shown before any PDF is generated */}
      {!objectUrl && !isLoading && !error && (
        <div style={contentStyle}>
          <p
            style={{
              textAlign: 'center',
              color: '#9ca3af',
              marginTop: `${PAGE_H_PX / 2 - MARGIN_TOP_PX - 48}px`,
            }}
          >
            Submit a pleading to preview it here.
            <br />
            <span style={{ fontSize: '13px' }}>
              Margins: 1 in top/left/bottom · 0.5 in right · 24 pt line height
              (CRC 2.111)
            </span>
          </p>
        </div>
      )}

      {/* Loading overlay */}
      {isLoading && (
        <div style={overlayStyle}>
          <span>Generating pleading…</span>
        </div>
      )}

      {/* Error overlay */}
      {error && !isLoading && (
        <div style={{ ...overlayStyle, background: 'rgba(255,255,255,0.93)' }}>
          <div style={{ textAlign: 'center', color: '#dc2626', maxWidth: '80%' }}>
            <strong>Error</strong>
            <br />
            {error}
          </div>
        </div>
      )}
    </div>
  );
}

export default PleadingPaperPreview;
