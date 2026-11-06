# Architecture

## Current State

The repository currently contains the project substrate only. Application components will be introduced through working vertical slices rather than speculative scaffolding.

## Planned Components

```text
React and TypeScript web interface
              ↓
       Python/FastAPI API
              ↓
          PostgreSQL
```

The initial workflow captures a posting URL, preserves source material, extracts structured facts with verbatim supporting source text, allows human correction and approval, and adds approved opportunities to a CRM.

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
