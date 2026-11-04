# 0003: PostgreSQL as the Source of Truth

- **Status:** Accepted
- **Date:** 2026-11-04

## Context

The system must preserve structured opportunities, requirement occurrences, candidate evidence, workflow history, and source provenance.

## Decision

Use PostgreSQL as the authoritative structured store. Add `pgvector` only when semantic retrieval is implemented and measured.

## Consequences

- Structured facts do not depend on a vector index.
- Schema migrations and backup compatibility become deployment concerns.
- Retrieval results must link back to authoritative records.
