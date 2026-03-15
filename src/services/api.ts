/**
 * API service for the Compass Outlaw FastAPI backend.
 */

/** Identity information about the pro per filer. */
export interface PleadingIdentity {
  name: string;
  address: string;
  phone?: string;
  email?: string;
}

/** Geographic/court information for the pleading. */
export interface PleadingGeo {
  court: string;
  county: string;
  state: string;
}

/** Full payload sent to /api/generate_pleading. */
export interface PleadingPayload {
  identity: PleadingIdentity;
  geo: PleadingGeo;
  /** Body content in Markdown format. */
  bodyMarkdown: string;
  /** Optional case identifier used for file naming. */
  caseId?: string;
}

// ── Full structured payload (matches backend engine expectations) ────────────

export interface GeoPage {
  width: number;
  height: number;
}

export interface GeoMargins {
  top: number;
}

export interface GeoLineNumbers {
  right_edge: number;
  rule_x: number;
  font_size: number;
}

export interface GeoTextArea {
  left: number;
  right: number;
}

export interface GeoTypography {
  body_size: number;
  line_height: number;
  lines_per_page: number;
  footer_size: number;
  footer_y: number;
}

export interface GeoCaption {
  separator_x: number;
  court_line: number;
  party_block_start: number;
  party_block_end: number;
  right_area_left: number;
}

export interface GeoClerkVoid {
  active_lines: number[];
  text_max_x: number;
}

export interface FullPleadingGeo {
  page: GeoPage;
  margins: GeoMargins;
  line_numbers: GeoLineNumbers;
  text_area: GeoTextArea;
  typography: GeoTypography;
  caption: GeoCaption;
  clerk_void: GeoClerkVoid;
}

export interface FullPleadingFiler {
  name: string;
  street_address: string;
  city_state_zip: string;
  telephone: string;
  email: string;
  role: string;
}

export interface FullPleadingCase {
  court_name: string;
  court_county: string;
  matter_type: string;
  petitioner_label: string;
  petitioner_name: string;
  respondent_label: string;
  respondent_name: string;
  case_number: string;
  document_title: string[];
}

export interface FullPleadingIdentity {
  filer: FullPleadingFiler;
  case: FullPleadingCase;
}

/**
 * Fully-structured payload matching the /api/generate_pleading endpoint's
 * engine schema (geo dictionary + nested identity + body_md).
 *
 * Use with {@link generateFullPleading}.
 */
export interface FullPleadingPayload {
  geo: FullPleadingGeo;
  identity: FullPleadingIdentity;
  body_md: string;
}

/**
 * Send a pleading payload to the backend and return the generated PDF as a
 * Blob.  The backend is expected to respond with Content-Type: application/pdf.
 *
 * @throws {Error} when the server returns a non-OK response.
 */
export async function generatePleading(payload: PleadingPayload): Promise<Blob> {
  const response = await fetch('/api/generate_pleading', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail: string;
    try {
      detail = await response.text();
    } catch {
      detail = response.statusText;
    }
    throw new Error(`Pleading generation failed (${response.status}): ${detail}`);
  }

  return response.blob();
}

/**
 * Send a fully-structured pleading payload (geo + identity + body_md) to the
 * backend and return the generated PDF as a Blob.
 *
 * This variant accepts the complete engine schema used by the Python PDF
 * renderer (content.py) rather than the simplified form fields.
 *
 * @throws {Error} when the server returns a non-OK response.
 */
export async function generateFullPleading(payload: FullPleadingPayload): Promise<Blob> {
  const response = await fetch('/api/generate_pleading', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    let detail: string;
    try {
      detail = await response.text();
    } catch {
      detail = response.statusText;
    }
    throw new Error(`Pleading generation failed (${response.status}): ${detail}`);
  }

  return response.blob();
}
