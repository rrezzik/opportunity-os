# Opportunity OS

Opportunity OS is an AI-assisted opportunity intelligence and job-search workflow. It is intended to make job searching easier to begin, more evidence-driven, and more useful over time.

> **Status:** Project substrate. The first planned vertical slice captures a job-posting URL and produces evidence-backed structured extraction for human review.

## Problem

Job searching requires repeatedly collecting fragmented postings, identifying meaningful requirements, judging fit, preparing truthful materials, and remembering what was learned during each interaction. The work is easy to avoid and difficult to improve when its evidence remains scattered.

Opportunity OS will provide two connected views:

- **Opportunity CRM:** capture, review, prepare, and track individual opportunities.
- **Market Intelligence:** aggregate approved postings to identify recurring capabilities, role families, and directional market signals.

## Initial User Flow

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

Application setup will be added with the first vertical slice. Prerequisites are currently:

- Docker with Docker Compose
- Git

Do not add real personal or application data to development fixtures.

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
