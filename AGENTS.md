# Project Instructions

## Product Principles

- Build useful vertical slices before broad infrastructure.
- Preserve source provenance for extracted facts and generated claims.
- Treat AI output as untrusted until validated and approved by a human.
- Never fabricate, infer as fact, or exaggerate candidate experience.
- Do not submit applications, send messages, or schedule interviews without explicit human approval.
- Optimize for relevance, evidence, and genuine connection rather than application volume.

## Architecture Boundaries

- The planned web client is React with TypeScript.
- The planned API and AI workflow layer is Python with FastAPI.
- PostgreSQL is the structured source of truth.
- Embeddings are a retrieval index, not an authoritative fact store.
- Add queues, orchestration frameworks, or distributed infrastructure only after documenting a demonstrated need.
- Keep public code and private runtime data strictly separated.

## Privacy and Security

- Never commit credentials, `.env` files, production data, résumés, career evidence, contacts, transcripts, tailored applications, or unredacted model traces.
- Use synthetic or carefully minimized fixtures.
- Do not log secrets, complete private source documents, or unnecessary personal information.
- Validate user-supplied URLs and prevent requests to private or link-local network resources.
- Preserve an audit trail for AI extraction, correction, approval, and generation.

## Development Workflow

- Keep changes small and reviewable.
- Use a feature branch and pull request for each bounded session.
- Update documentation when behavior, architecture, commands, or privacy boundaries change.
- Add or update tests with every behavior change.
- Do not edit generated files manually.
- Record meaningful architectural decisions in `docs/decisions`.

## Verification

Run the repository checks documented in `README.md` before requesting review. As the application is introduced, this section must be updated with exact formatting, linting, type-checking, test, and build commands.

A change is complete only when:

- The stated user-visible outcome works.
- Relevant tests pass.
- Source provenance and privacy constraints are preserved.
- Documentation accurately reflects the current implementation.
- No unrelated scope has been added.
