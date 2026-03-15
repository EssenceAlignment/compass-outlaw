import { useState } from 'react';
import { generatePleading, generateFullPleading, type PleadingPayload } from './services/api';
import { generateFileName } from './utils/fileNaming';
import { PleadingPaperPreview } from './components/PleadingPaperPreview';
import { jonesVHartPayload } from './data/mockComplaintPayload';

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontWeight: 600,
  marginBottom: '4px',
  fontSize: '13px',
  color: '#374151',
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  fontSize: '14px',
  boxSizing: 'border-box',
  fontFamily: 'inherit',
};

const fieldsetStyle: React.CSSProperties = {
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '12px 16px',
  marginBottom: '16px',
};

const legendStyle: React.CSSProperties = {
  fontWeight: 700,
  fontSize: '12px',
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
  color: '#6b7280',
  padding: '0 4px',
};

function Field({
  label,
  id,
  value,
  onChange,
  required,
  placeholder,
}: {
  label: string;
  id: string;
  value: string;
  onChange: (v: string) => void;
  required?: boolean;
  placeholder?: string;
}) {
  return (
    <div style={{ marginBottom: '12px' }}>
      <label htmlFor={id} style={labelStyle}>
        {label}
        {required && <span style={{ color: '#ef4444' }}> *</span>}
      </label>
      <input
        id={id}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        required={required}
        placeholder={placeholder}
        style={inputStyle}
      />
    </div>
  );
}

function App() {
  // ── Identity ──────────────────────────────────────────────────────────────
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');

  // ── Geo / Court ───────────────────────────────────────────────────────────
  const [court, setCourt] = useState('');
  const [county, setCounty] = useState('');
  const [state, setState] = useState('CA');

  // ── Document ──────────────────────────────────────────────────────────────
  const [caseId, setCaseId] = useState('');
  const [fileType, setFileType] = useState('');
  const [description, setDescription] = useState('');
  const [bodyMarkdown, setBodyMarkdown] = useState('');

  // ── State ─────────────────────────────────────────────────────────────────
  const [pdfBlob, setPdfBlob] = useState<Blob | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadName, setDownloadName] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setPdfBlob(null);
    setDownloadName(null);

    const payload: PleadingPayload = {
      identity: { name, address, phone: phone || undefined, email: email || undefined },
      geo: { court, county, state },
      bodyMarkdown,
      caseId: caseId || undefined,
    };

    try {
      const blob = await generatePleading(payload);
      const fileName = await generateFileName(
        caseId || 'UNKNOWN',
        fileType || 'Pleading',
        description || 'Document',
      );
      setPdfBlob(blob);
      setDownloadName(fileName);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  }

  async function handleTestRender() {
    setIsLoading(true);
    setError(null);
    setPdfBlob(null);
    setDownloadName(null);

    try {
      const blob = await generateFullPleading(jonesVHartPayload);
      const { filer, case: caseInfo } = jonesVHartPayload.identity;
      const fileName = await generateFileName(
        caseInfo.case_number,
        'Complaint',
        filer.name.replace(/\s+/g, '_'),
      );
      setPdfBlob(blob);
      setDownloadName(fileName);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setIsLoading(false);
    }
  }

  function handleDownload() {
    if (!pdfBlob || !downloadName) return;
    const url = URL.createObjectURL(pdfBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = downloadName;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div
      style={{
        display: 'flex',
        gap: '32px',
        padding: '32px',
        minHeight: '100vh',
        background: '#f9fafb',
        fontFamily: 'system-ui, sans-serif',
        boxSizing: 'border-box',
        alignItems: 'flex-start',
      }}
    >
      {/* ── Form panel ──────────────────────────────────────────────────── */}
      <div
        style={{
          width: '360px',
          flexShrink: 0,
          background: '#fff',
          borderRadius: '12px',
          border: '1px solid #e5e7eb',
          padding: '24px',
          boxSizing: 'border-box',
        }}
      >
        <h1
          style={{
            margin: '0 0 4px',
            fontSize: '20px',
            fontWeight: 700,
            color: '#111827',
          }}
        >
          Compass Outlaw
        </h1>
        <p
          style={{ margin: '0 0 24px', fontSize: '13px', color: '#6b7280' }}
        >
          Pro Per Pleading Generator
        </p>

        {/* ── Test Render button ─────────────────────────────────────── */}
        <button
          type="button"
          onClick={handleTestRender}
          disabled={isLoading}
          style={{
            width: '100%',
            padding: '10px',
            marginBottom: '20px',
            background: isLoading ? '#9ca3af' : '#7c3aed',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: 600,
            cursor: isLoading ? 'not-allowed' : 'pointer',
          }}
        >
          {isLoading ? 'Generating…' : '⚡ Test Render — Jones v. Hart'}
        </button>

        <hr style={{ border: 'none', borderTop: '1px solid #e5e7eb', margin: '0 0 20px' }} />

        <form onSubmit={handleSubmit}>
          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>Identity</legend>
            <Field label="Full Name" id="name" value={name} onChange={setName} required />
            <Field label="Address" id="address" value={address} onChange={setAddress} required />
            <Field label="Phone" id="phone" value={phone} onChange={setPhone} placeholder="Optional" />
            <Field label="Email" id="email" value={email} onChange={setEmail} placeholder="Optional" />
          </fieldset>

          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>Court</legend>
            <Field label="Court Name" id="court" value={court} onChange={setCourt} required />
            <Field label="County" id="county" value={county} onChange={setCounty} required />
            <Field label="State" id="state" value={state} onChange={setState} required />
          </fieldset>

          <fieldset style={fieldsetStyle}>
            <legend style={legendStyle}>Document</legend>
            <Field label="Case ID" id="caseId" value={caseId} onChange={setCaseId} placeholder="e.g. 24CV123456" />
            <Field label="File Type" id="fileType" value={fileType} onChange={setFileType} placeholder="e.g. Motion" />
            <Field label="Description" id="description" value={description} onChange={setDescription} placeholder="e.g. SummaryJudgment" />
          </fieldset>

          <div style={{ marginBottom: '16px' }}>
            <label htmlFor="bodyMarkdown" style={labelStyle}>
              Body (Markdown) <span style={{ color: '#ef4444' }}>*</span>
            </label>
            <textarea
              id="bodyMarkdown"
              value={bodyMarkdown}
              onChange={(e) => setBodyMarkdown(e.target.value)}
              required
              rows={10}
              placeholder="# Motion&#10;&#10;Plaintiff respectfully moves the court..."
              style={{
                ...inputStyle,
                resize: 'vertical',
                lineHeight: '1.5',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '10px',
              background: isLoading ? '#9ca3af' : '#1d4ed8',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: isLoading ? 'not-allowed' : 'pointer',
            }}
          >
            {isLoading ? 'Generating…' : 'Generate Pleading'}
          </button>
        </form>

        {pdfBlob && downloadName && (
          <button
            onClick={handleDownload}
            style={{
              marginTop: '12px',
              width: '100%',
              padding: '10px',
              background: '#059669',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ⬇ Download PDF
          </button>
        )}

        {downloadName && (
          <p
            style={{
              marginTop: '8px',
              fontSize: '11px',
              color: '#6b7280',
              wordBreak: 'break-all',
            }}
          >
            {downloadName}
          </p>
        )}
      </div>

      {/* ── Preview panel ────────────────────────────────────────────────── */}
      <div style={{ overflowX: 'auto' }}>
        <PleadingPaperPreview
          pdfBlob={pdfBlob}
          isLoading={isLoading}
          error={error}
        />
      </div>
    </div>
  );
}

export default App;
