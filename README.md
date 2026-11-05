# Opportunity OS

Opportunity OS is an AI-assisted opportunity intelligence and job-search workflow. It is intended to make job searching easier to begin, more evidence-driven, and more useful over time.

> **Status:** Local extraction spike. The current vertical slice fetches one of two explicitly approved public job postings, creates a manual OpenCode extraction prompt, validates the returned JSON, and displays each extracted claim with supporting evidence for human review.

## Problem

Job searching requires repeatedly collecting fragmented postings, identifying meaningful requirements, judging fit, preparing truthful materials, and remembering what was learned during each interaction. The work is easy to avoid and difficult to improve when its evidence remains scattered.

Opportunity OS will provide two connected views:

- **Opportunity CRM:** capture, review, prepare, and track individual opportunities.
- **Market Intelligence:** aggregate approved postings to identify recurring capabilities, role families, and directional market signals.

## Target User Flow

```text
Open web interface
→ paste job-listing URL
→ preserve posting snapshot
→ extract structured information with supporting text
→ correct inaccurate extraction
→ approve record
→ add opportunity to CRM
→ contribute approved requirements to Market Intelligence
```

Every extracted fact should remain traceable to the source posting. AI output is a draft until a human approves it.

## Current Extraction Spike

The implemented local flow deliberately stops before persistence, correction history, approval, CRM ingestion, and Market Intelligence aggregation:

```text
Approved posting URL
→ browser-compatible server fetch
→ in-memory source cleaning
→ Copy Prompt
→ manual OpenCode inference
→ Paste JSON
→ strict schema and source-URL validation
→ evidence review
```

The API accepts only the Fellow Software Engineer and Multiview Software Developer URLs encoded in [`apps/api/app/services.py`](apps/api/app/services.py). This narrow allowlist prevents the server from acting as a general-purpose URL fetcher. Fetched HTML, cleaned source, prompts, and model output are not persisted by this spike.

## Planned Architecture

- React and TypeScript web interface
- Python and FastAPI API
- PostgreSQL as the structured source of truth
- `pgvector` only where semantic retrieval adds demonstrated value
- Docker Compose for local development
- GitHub Actions for CI/CD

See [`docs/architecture.md`](docs/architecture.md) and the architecture decision records in [`docs/decisions`](docs/decisions).

## Current Roadmap

1. Establish the public project substrate and privacy boundary.
2. Capture one posting URL and display evidence-backed extraction.
3. Add trustworthy extraction contracts, persistence, review, and approval.
4. Add the CRM pipeline.
5. Build a reviewed posting corpus and Market Intelligence view.
6. Add private candidate evidence, retrieval, truthful tailoring, and evaluations.
7. Add application and interview workflows.
8. Deploy with observable and reversible CI/CD.

## Privacy Boundary

The codebase is public. Runtime career data is private.

The repository may contain source code, synthetic fixtures, architecture decisions, evaluation methodology, and aggregate demonstrations. It must not contain résumés, private career evidence, contacts, transcripts, production databases, credentials, tailored application artifacts, or unredacted model traces.

See [`SECURITY.md`](SECURITY.md) for reporting and data-handling expectations.

## Local Development

Prerequisites:

- Docker with Docker Compose
- Git

Do not add real personal or application data to development fixtures.

Start the local stack from the repository root:

```bash
docker compose up --build
```

Open the web interface at <http://localhost:5173>. The FastAPI service and interactive API documentation are available at <http://localhost:8000> and <http://localhost:8000/docs>.

### Manual OpenCode handoff

1. Keep or paste one of the approved posting URLs and select **Fetch**.
2. Review the cleaned source, then select **Copy prompt**.
3. Paste the prompt into a new OpenCode request. Do not add private candidate or application data.
4. Copy the JSON-only response into **OpenCode JSON response**.
5. Select **Validate and display**.
6. Review every extracted value against its quotation. Validation confirms the JSON contract and source URL, not factual correctness.

This handoff is intentionally manual: the application does not expose OpenCode as a local network service and does not require a paid model API.

Stop the stack with:

```bash
docker compose down
```

## Verification

Run these checks from the repository root before requesting review:

```bash
docker compose config
docker compose build
docker compose run --rm api pytest -q
docker compose run --rm web npm run build
git diff --check
```

For a live smoke test, start the stack and confirm that `/health`, the web interface, the approved Fellow fetch, malformed extraction rejection, and valid extraction display all work.

## Non-Goals

The initial system will not:

- Automatically submit applications or send messages
- Fabricate or exaggerate candidate evidence
- Circumvent job-source terms or access controls
- Optimize for mass-application volume
- Introduce orchestration infrastructure before a concrete bottleneck exists

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md).

## License

Licensed under the [Apache License 2.0](LICENSE).
