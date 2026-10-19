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
pip install -e ".[dev]"
ruff check .
pytest
```

Keep pull requests small and focused. Only use public APIs that need no login.
