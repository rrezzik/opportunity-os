# 0001: Public Code and Private Runtime Data

- **Status:** Accepted
- **Date:** 2026-11-04

## Context

Opportunity OS should demonstrate engineering work publicly while processing sensitive career, contact, and application information.

## Decision

Publish application code, architecture, synthetic fixtures, and privacy-safe demonstrations. Keep all personal and operational data in ignored local or private production storage.

## Consequences

- Public CI must use synthetic data.
- Logs, prompts, traces, and fixtures require privacy review.
- Portfolio demonstrations cannot depend on access to production data.
