/**
 * File naming utility for Compass Outlaw.
 *
 * Convention: YYYY-MM-DD_[CaseID]_[FileType]_[Description]_[Hash8].pdf
 *
 * Example:
 *   2026-03-15_24CV123456_Motion_SummaryJudgment_a1b2c3d4.pdf
 */

/**
 * Replace any character that is not alphanumeric or a hyphen with an
 * underscore, and collapse consecutive underscores to one.
 */
function sanitizeSegment(segment: string): string {
  return segment
    .replace(/[^a-zA-Z0-9-]/g, '_')
    .replace(/_+/g, '_')
    .replace(/^_|_$/g, '');
}

/**
 * Return the first 8 hex characters of the SHA-256 digest of `input`.
 * Falls back to a timestamp-based pseudo-hash when SubtleCrypto is
 * unavailable (e.g., non-HTTPS environments in older browsers).
 */
async function computeHash8(input: string): Promise<string> {
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    const data = new TextEncoder().encode(input);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('')
      .slice(0, 8);
  }
  // Fallback: simple djb2-style hash converted to hex
  let hash = 5381;
  for (let i = 0; i < input.length; i++) {
    hash = ((hash << 5) + hash) ^ input.charCodeAt(i);
    hash = hash >>> 0; // keep unsigned 32-bit
  }
  return hash.toString(16).padStart(8, '0').slice(0, 8);
}

/**
 * Generate a court-document filename following the strict Compass Outlaw
 * naming convention.
 *
 * @param caseId      - Case identifier, e.g. "24CV123456"
 * @param fileType    - Document type, e.g. "Motion" or "Opposition"
 * @param description - Short description, e.g. "SummaryJudgment"
 * @param hashSource  - Optional string to hash; defaults to
 *                      caseId + fileType + description + today's date.
 * @returns           Promise resolving to a filename string ending in ".pdf".
 */
export async function generateFileName(
  caseId: string,
  fileType: string,
  description: string,
  hashSource?: string,
): Promise<string> {
  const date = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
  const source = hashSource ?? `${caseId}|${fileType}|${description}|${date}`;
  const hash = await computeHash8(source);

  const segments = [
    date,
    sanitizeSegment(caseId),
    sanitizeSegment(fileType),
    sanitizeSegment(description),
    hash,
  ];

  return `${segments.join('_')}.pdf`;
}
