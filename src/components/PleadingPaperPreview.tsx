import React from 'react';

/**
 * PleadingPaperPreview
 *
 * Renders a deterministic visual representation of a standard California legal
 * pleading page (8.5 × 11 inches) with strict typographic geometry:
 *
 *   - Page size:    8.5 in × 11 in  (at 96 dpi: 816 px × 1056 px)
 *   - Top margin:   1.0 in (72 pt / 96 px)
 *   - Left margin:  1.0 in (96 px)
 *   - Right margin: 0.5 in (48 px)
 *   - Base font:    Times New Roman, 12 pt
 */
const PleadingPaperPreview: React.FC<{ children?: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div style={pageStyle}>
      <div style={contentAreaStyle}>
        {children ?? <DefaultContent />}
      </div>
    </div>
  );
};

/* ─── Default placeholder content ─────────────────────────────────────────── */

const DefaultContent: React.FC = () => (
  <>
    <p style={{ marginBottom: '1em' }}>
      [Party Name, Pro Per]
      <br />
      [Street Address]
      <br />
      [City, State ZIP]
      <br />
      [Phone Number]
    </p>

    <p style={{ textAlign: 'center', fontWeight: 'bold', marginBottom: '1em' }}>
      SUPERIOR COURT OF THE STATE OF CALIFORNIA
      <br />
      FOR THE COUNTY OF [COUNTY]
    </p>

    <p style={{ marginBottom: '0.5em' }}>
      <strong>[PLAINTIFF NAME],</strong>
    </p>
    <p style={{ paddingLeft: '2em', marginBottom: '0.5em' }}>Plaintiff,</p>
    <p style={{ marginBottom: '0.5em' }}>vs.</p>
    <p style={{ marginBottom: '0.5em' }}>
      <strong>[DEFENDANT NAME],</strong>
    </p>
    <p style={{ paddingLeft: '2em', marginBottom: '1em' }}>Defendant.</p>

    <p>Case No.: _______________</p>
  </>
);

/* ─── Strict geometry styles ───────────────────────────────────────────────── */

/**
 * 8.5 in × 11 in at 96 dpi  →  816 px × 1056 px
 */
const pageStyle: React.CSSProperties = {
  width: '816px',    /* 8.5 in × 96 dpi */
  height: '1056px',  /* 11 in  × 96 dpi */
  backgroundColor: '#ffffff',
  boxShadow: '0 4px 24px rgba(0, 0, 0, 0.18)',
  position: 'relative',
  boxSizing: 'border-box',
  overflow: 'hidden',
  /* Top margin: 1.0 in = 72 pt = 96 px  */
  paddingTop: '96px',
  /* Left margin: 1.0 in = 96 px  */
  paddingLeft: '96px',
  /* Right margin: 0.5 in = 48 px  */
  paddingRight: '48px',
  /* Bottom margin: 1.0 in (conventional) = 96 px */
  paddingBottom: '96px',
};

/**
 * The writable text area inside the margins.
 * Font: Times New Roman, 12 pt (16 px at 96 dpi).
 */
const contentAreaStyle: React.CSSProperties = {
  fontFamily: "'Times New Roman', Times, serif",
  fontSize: '16px',   /* 12 pt at 96 dpi  (12 × 96/72 ≈ 16 px) */
  lineHeight: '2',    /* double-spaced, standard for CA pleadings */
  color: '#000000',
  width: '100%',
  height: '100%',
  boxSizing: 'border-box',
};

export default PleadingPaperPreview;
