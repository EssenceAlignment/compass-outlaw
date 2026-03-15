import { type FullPleadingPayload } from '../services/api';

/**
 * Deterministic test payload for the Jones v. Hart Unlimited Complaint.
 *
 * Geo coordinates follow standard 8.5 × 11 inch page dimensions
 * (612 × 792 points), with a 72 pt top margin and 24 pt line height
 * to satisfy CRC 2.111 compliance requirements.
 *
 * The body_md field uses exact Markdown structure required by the Python
 * PDF engine (content.py) for word-wrapping and line-height calculations.
 */
export const jonesVHartPayload: FullPleadingPayload = {
  geo: {
    page: { width: 612.0, height: 792.0 },
    margins: { top: 72.0 },
    line_numbers: { right_edge: 45.0, rule_x: 54.0, font_size: 12.0 },
    text_area: { left: 72.0, right: 576.0 },
    typography: { body_size: 12.0, line_height: 24.0, lines_per_page: 28, footer_size: 10.0, footer_y: 36.0 },
    caption: { separator_x: 324.0, court_line: 8, party_block_start: 11, party_block_end: 22, right_area_left: 334.0 },
    clerk_void: { active_lines: [1, 2, 3, 4, 5, 6, 7], text_max_x: 350.0 },
  },
  identity: {
    filer: {
      name: "ERIC BRAKEBILL JONES",
      street_address: "5634 Noel Drive",
      city_state_zip: "Temple City, CA 91780",
      telephone: "(626) 348-3019",
      email: "eric@recovery-compass.org",
      role: "Plaintiff In Pro Per",
    },
    case: {
      court_name: "SUPERIOR COURT OF THE STATE OF CALIFORNIA",
      court_county: "COUNTY OF LOS ANGELES",
      matter_type: "UNLIMITED CIVIL CASE",
      petitioner_label: "Plaintiff",
      petitioner_name: "ERIC BRAKEBILL JONES,\nan individual",
      respondent_label: "Defendant",
      respondent_name: "KATHY HART, an individual",
      case_number: "[UNASSIGNED]",
      document_title: [
        "COMPLAINT FOR DAMAGES:",
        "(1) FRAUD & DECEIT (INTENTIONAL)",
        "(2) BREACH OF CONTRACT",
        "(3) COMMON COUNTS (MONEY PAID)",
        "(4) CONVERSION",
        "(5) INTENTIONAL INFLICTION OF EMOTIONAL",
        "DISTRESS",
        "",
        "DEMAND: $115,422.54",
      ],
    },
  },
  body_md: `**1. JURISDICTION (UNLIMITED):** Plaintiff is a resident of Los Angeles County. Defendant Kathy Hart resides in Texas but solicited Plaintiff's services in California, creating specific jurisdiction. The amount in controversy exceeds $35,000.

**2. GENERAL ALLEGATIONS (THE TRAP):** On August 13, 2025, at Defendant's urgent request, Plaintiff traveled to Texas to provide emergency caretaking and IT security services. Defendant fraudulently concealed her medical timeline, specifically an undisclosed second surgery and extended rehabilitation, to trap Plaintiff in Texas as an unpaid 24/7 caretaker until September 3, 2025.

**3. DAMAGES (BUSINESS LOSS):** Due to Defendant's negligence and deceit, Plaintiff was unable to return to his business (Recovery Compass) in California, resulting in lost revenue and operational expenses estimated at $75,000.00.

**4. FINANCIAL ABUSE:** Defendant claimed inability to access funds and coerced Plaintiff to pay her replacement caretaker, Amy McCellon, via Venmo from Plaintiff's personal funds. Defendant has failed to reimburse these advances.

**5. CONVERSION (IT THEFT):** Plaintiff secured Defendant's digital infrastructure, created accounts (kathyandkent1947@gmail.com), and retained counsel (Ramey & Flock) for her benefit. Defendant utilizes this 'Project Hydra' IP without compensation.

**6. CONSENT TO RECORD:** Plaintiff possesses audio evidence of Defendant's admissions, recorded with Defendant's express consent.

PRAYER: Judgment for $19,422.54 (Services) + $75,000 (Business Loss) + $21,000 (Punitive/Emotional Distress). TOTAL: $115,422.54.

Dated: January 20, 2026

___
ERIC BRAKEBILL JONES, Plaintiff`,
};
