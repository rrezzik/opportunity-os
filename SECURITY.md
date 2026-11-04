# Security Policy

## Reporting

Do not open a public issue containing a vulnerability, credential, personal record, private job-search artifact, or production detail. Report sensitive concerns privately to the repository owner through GitHub.

## Data Classification

The public repository may contain code, synthetic fixtures, architecture decisions, and aggregate demonstrations.

The following are private and must remain outside Git history and public CI logs:

- API keys and credentials
- Résumés and candidate evidence
- Contact, recruiter, and interview records
- Captured transcripts or private notes
- Production databases and backups
- Tailored application artifacts
- Unredacted prompts, traces, and model responses containing private data

## Development Expectations

- Use environment variables or approved secret storage.
- Use synthetic or minimized fixtures.
- Validate externally supplied URLs before fetching them.
- Keep dependencies patched and review automated updates.
- Require human approval for consequential external actions.
