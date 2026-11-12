# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/). Commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

## [0.2.0] - 2026-11-12

### Added
- Website: newest jobs first, posted dates, a "New" badge, an age filter, saved jobs and
  filters kept in the URL so searches can be shared.
- Seniority filter (intern, junior, mid, senior, lead, manager) in the CLI (`--level`),
  the profile (`levels`) and the website, with color-coded badges.
- Teamtailor, BambooHR and Breezy connectors, and the open job feeds Remote OK, Remotive,
  Arbeitnow and We Work Remotely.
- Accent-insensitive search, city aliases (such as BCN) and `jobradar stats`.
- More than 300 companies in `companies.yaml`.
- Quality gate in CI: ruff lint and format, mypy, tests on Python 3.10 to 3.13 with a
  coverage minimum, package build, CodeQL.
- pre-commit hooks, Dependabot, a security policy and code owners.
- Release workflow that publishes a GitHub release for every version tag.

### Changed
- `jobradar check` reports ATS server errors (5xx) as warnings instead of failures.
- Workflows run with minimal permissions, concurrency limits and timeouts; HTTP requests
  send a JobRadar User-Agent; alerts are capped at 10 messages per run.

### Removed
- Companies whose job boards no longer exist (Aircall, Doctolib and others).

## [0.1.0] - 2026-10-19

### Added
- First version: Greenhouse, Lever, Ashby, Workable, Recruitee, Personio and
  SmartRecruiters connectors.
- `jobradar search`, `check`, `find`, `update` and `export` commands.
- SQLite storage with alerts only for new jobs, a profile filter, and Discord and Telegram
  notifications from a daily GitHub Actions workflow.
- Static job board on GitHub Pages, rebuilt every day.
- Contributing guide, issue and pull request templates.

[Unreleased]: https://github.com/dabupr/JobRadar/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/dabupr/JobRadar/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/dabupr/JobRadar/releases/tag/v0.1.0
