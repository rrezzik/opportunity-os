import { FormEvent, useState } from "react";

import type {
  EvidenceItem,
  EvidenceText,
  PostingExtraction,
  ProvisionalDraft,
  SourcePackage,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const FELLOW_URL =
  "https://techjobfinder.investottawa.ca/companies/fellow-2-842f8800-77a3-4e17-a03e-fdba3aeea256/jobs/97059938-software-engineer#content";

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    return body.detail ?? `Request failed with status ${response.status}.`;
  } catch {
    return `Request failed with status ${response.status}.`;
  }
}

function ScalarField({ label, evidence }: { label: string; evidence: EvidenceText }) {
  return (
    <article className="evidence-card">
      <p className="eyebrow">{label}</p>
      <p className={evidence.value ? "value" : "value missing"}>
        {evidence.value ?? "Not provided"}
      </p>
      {evidence.confidence && (
        <p className="confidence">Model confidence: {evidence.confidence}</p>
      )}
      {evidence.supporting_source_text && (
        <blockquote>“{evidence.supporting_source_text}”</blockquote>
      )}
    </article>
  );
}

function EvidenceList({ label, items }: { label: string; items: EvidenceItem[] }) {
  return (
    <section className="list-section">
      <h3>{label}</h3>
      {items.length === 0 ? (
        <p className="missing">None provided</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={`${item.value}-${index}`}>
              <strong>{item.value}</strong>
              <p className="confidence">Model confidence: {item.confidence}</p>
              <blockquote>“{item.supporting_source_text}”</blockquote>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default function App() {
  const [url, setUrl] = useState(FELLOW_URL);
  const [source, setSource] = useState<SourcePackage | null>(null);
  const [rawJson, setRawJson] = useState("");
  const [extraction, setExtraction] = useState<PostingExtraction | null>(null);
  const [draft, setDraft] = useState<ProvisionalDraft | null>(null);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function fetchSource(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setStatus("Fetching and cleaning the approved posting…");
    setSource(null);
    setExtraction(null);
    setDraft(null);
    try {
      const response = await fetch(`${API_URL}/api/source`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      if (!response.ok) throw new Error(await errorMessage(response));
      const data = (await response.json()) as SourcePackage;
      setSource(data);
      setStatus("Source ready. Copy the prompt into OpenCode.");
    } catch (caught) {
      setStatus("");
      setError(caught instanceof Error ? caught.message : "The source could not be fetched.");
    } finally {
      setLoading(false);
    }
  }

  async function copyPrompt() {
    if (!source) return;
    try {
      await navigator.clipboard.writeText(source.prompt);
      setStatus("Prompt copied. Run it in OpenCode, then paste the JSON response below.");
    } catch {
      setError("The browser could not copy the prompt. Select it manually instead.");
    }
  }

  async function validateExtraction(event: FormEvent) {
    event.preventDefault();
    if (!source) return;
    setLoading(true);
    setError("");
    setStatus("Validating the extraction shape…");
    try {
      const response = await fetch(`${API_URL}/api/extractions/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          capture_id: source.id,
          raw_json: rawJson,
        }),
      });
      if (!response.ok) throw new Error(await errorMessage(response));
      const data = (await response.json()) as ProvisionalDraft;
      setDraft(data);
      setExtraction(data.extraction);
      setStatus(
        "Provisional draft saved. Review every value against its supporting source text.",
      );
    } catch (caught) {
      setExtraction(null);
      setStatus("");
      setError(caught instanceof Error ? caught.message : "The extraction was invalid.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header className="hero">
        <p className="kicker">Opportunity OS · Extraction spike</p>
        <h1>Turn a job posting into reviewable evidence.</h1>
        <p>
          Fetch one approved public posting, run a transparent manual OpenCode handoff,
          and inspect every extracted claim beside its supporting source text.
        </p>
      </header>

      <section className="panel">
        <div className="step"><span>1</span> Fetch source</div>
        <form onSubmit={fetchSource} className="stack">
          <label htmlFor="source-url">Approved posting URL</label>
          <div className="input-row">
            <input
              id="source-url"
              type="url"
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              required
            />
            <button type="submit" disabled={loading}>Fetch</button>
          </div>
        </form>
      </section>

      {source && (
        <section className="panel">
          <div className="step"><span>2</span> Run in OpenCode</div>
          <p className="source-meta">
            <strong>{source.source_label}</strong> · {source.source_identifier}
          </p>
          <p className="source-meta">
            Capture {source.id} saved with raw source preserved separately (
            {source.raw_source.length.toLocaleString()} characters).
          </p>
          <details>
            <summary>Preview cleaned source</summary>
            <pre>{source.cleaned_source}</pre>
          </details>
          <textarea aria-label="Extraction prompt" value={source.prompt} readOnly rows={12} />
          <button type="button" className="secondary" onClick={copyPrompt}>
            Copy prompt
          </button>
        </section>
      )}

      {source && (
        <section className="panel">
          <div className="step"><span>3</span> Validate result</div>
          <form onSubmit={validateExtraction} className="stack">
            <label htmlFor="model-json">OpenCode JSON response</label>
            <textarea
              id="model-json"
              value={rawJson}
              onChange={(event) => setRawJson(event.target.value)}
              placeholder="Paste JSON only"
              rows={12}
              required
            />
            <button type="submit" disabled={loading}>Validate and save draft</button>
          </form>
        </section>
      )}

      {(status || error) && (
        <div className={error ? "notice error" : "notice"} role="status">
          {error || status}
        </div>
      )}

      {extraction && (
        <section className="results">
          <div className="results-heading">
            <p className="kicker">Provisional extraction</p>
            <h2>{extraction.title.value ?? "Untitled role"}</h2>
            {draft && <p>Saved provisional draft · {draft.id}</p>}
            <a href={extraction.source_url} target="_blank" rel="noreferrer">
              Review original posting ↗
            </a>
          </div>
          <div className="evidence-grid">
            <ScalarField label="Title" evidence={extraction.title} />
            <ScalarField label="Company" evidence={extraction.company} />
            <ScalarField label="Location" evidence={extraction.location} />
            <ScalarField label="Compensation" evidence={extraction.compensation} />
            <ScalarField label="Employment type" evidence={extraction.employment_type} />
            <ScalarField label="Posting date" evidence={extraction.posting_date} />
            <ScalarField label="Work arrangement" evidence={extraction.work_arrangement} />
            <ScalarField label="Seniority" evidence={extraction.seniority} />
            <ScalarField label="Role family" evidence={extraction.suggested_role_family} />
          </div>
          <EvidenceList label="Responsibilities" items={extraction.responsibilities} />
          <EvidenceList label="Required qualifications" items={extraction.required_qualifications} />
          <EvidenceList label="Preferred qualifications" items={extraction.preferred_qualifications} />
          <EvidenceList label="Technologies" items={extraction.technologies} />
        </section>
      )}
    </main>
  );
}
