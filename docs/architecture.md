# Architecture

## Current State

The current vertical slice uses React and FastAPI to capture one allowlisted public
posting, preserve its source in PostgreSQL, validate a manually produced OpenCode
extraction against the server-owned canonical source, and save a provisional draft.

## Components

```text
React and TypeScript web interface
              ↓
       Python/FastAPI API
              ↓
          PostgreSQL
```

`posting_captures` stores immutable capture provenance: URL, source identifier,
capture time, raw source, canonical cleaned source, source format version, and raw
content SHA-256. `extraction_drafts` stores the capture foreign key, extraction
schema version, validated structured JSON, provisional status, and creation time.
PostgreSQL is authoritative; the browser supplies only a capture ID and candidate
JSON when requesting validation.

The API exposes capture creation/retrieval and provisional extraction
creation/retrieval. Correction, approval, CRM ingestion, aggregation, and
embeddings remain outside this slice.

Market Intelligence is an aggregate view over approved requirement occurrences. It does not replace the individual opportunity workflow and must preserve links to every source occurrence.

## Trust Model

- External postings are untrusted input.
- AI extraction is an untrusted draft.
- Human approval controls entry into the trusted market corpus.
- PostgreSQL and retained sources are authoritative.
- Embeddings may assist retrieval but never establish factual truth.
- Consequential external actions require explicit human approval.

## Public and Private Boundary

The application code and synthetic demonstrations are public. Personal candidate evidence and operational job-search data are private runtime data and must not enter Git history or public CI.
