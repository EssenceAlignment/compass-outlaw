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
