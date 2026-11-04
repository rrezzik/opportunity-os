# 0002: React and FastAPI

- **Status:** Accepted
- **Date:** 2026-11-04

## Context

The project needs an interactive CRM interface and an AI-oriented API layer while creating relevant full-stack portfolio evidence.

## Decision

Use React with TypeScript for the web interface and Python with FastAPI for the API and AI workflows.

## Consequences

- The repository will contain separate web and API components.
- Shared contracts require explicit versioning and validation.
- Docker Compose will provide a consistent local environment.
