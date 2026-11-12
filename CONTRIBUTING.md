# Contributing to JobRadar

The most useful contribution is **adding a company**. It takes two minutes.

## Add a company

1. Open the company's careers page and look at the URL of its job board:

   | ATS | URL looks like | `slug` |
   |---|---|---|
   | greenhouse | `boards.greenhouse.io/acme` | `acme` |
   | lever | `jobs.lever.co/acme` | `acme` |
   | ashby | `jobs.ashbyhq.com/acme` | `acme` |
   | workable | `apply.workable.com/acme` | `acme` |
   | recruitee | `acme.recruitee.com` | `acme` |
   | personio | `acme.jobs.personio.de` | `acme` |
   | smartrecruiters | `jobs.smartrecruiters.com/Acme` | `Acme` (case matters) |

   Not sure which one it uses? `jobradar find "Acme"` tries the usual ids on every ATS.

2. Add one line to [`companies.yaml`](companies.yaml):

   ```yaml
   - { name: Acme, ats: lever, slug: acme, city: Barcelona }
   ```

3. Run `jobradar check`. Every company must print `ok`. The same check runs in CI.

Companies with a hub in Barcelona and Catalonia are especially welcome.

## Add support for another ATS

Connectors live in `src/jobradar/connectors/`. Copy a small one (for example `lever.py`),
split it into a `parse_*` function that turns the API response into `Job` objects and a
`fetch_*` function that does the HTTP call, register it in `connectors/__init__.py`, and
add a test in `tests/test_connectors.py` using a trimmed sample of the real response.

## Development

```bash
git clone https://github.com/dabupr/JobRadar && cd JobRadar
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install          # runs ruff, ruff format and mypy before every commit
pytest                      # tests with coverage
```

Every pull request runs the same checks in CI: lint and format (ruff), types (mypy), tests
on Python 3.10 to 3.13 with a minimum coverage, a package build, and CodeQL. A PR can only
be merged when they are green.

### Workflow

1. Create a branch from `main`: `feat/short-name`, `fix/short-name`, `docs/...`, `ci/...`.
2. Keep pull requests small and focused, with tests for new behaviour.
3. Use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages and
   PR titles, for example `feat: add Workday connector` or `fix(lever): handle empty
   location`. Release notes are generated from them.
4. Only use public APIs that need no login.

### Project layout

| Path | What lives there |
| --- | --- |
| `src/jobradar/connectors/` | one module per ATS: `parse_*` (pure) and `fetch_*` (HTTP) |
| `src/jobradar/feeds.py` | open job boards (Remote OK, Remotive...) |
| `src/jobradar/cli.py` | the `jobradar` command |
| `src/jobradar/site.py`, `web/` | the static website |
| `companies.yaml` | the list of watched companies |
| `.github/workflows/` | CI, CodeQL, daily alerts and the Pages deploy |
