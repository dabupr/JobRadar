# JobRadar

[![CI](https://github.com/dabupr/JobRadar/actions/workflows/ci.yml/badge.svg)](https://github.com/dabupr/JobRadar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Job alerts straight from company career pages. No scraping of job boards, no API keys, no blocks.**

Most companies publish their openings through an applicant tracking system (ATS) such as
Greenhouse, Lever or Ashby, and those systems have public APIs. JobRadar reads them
directly for a list of companies you can extend with a one-line pull request, so you see
new jobs the day they appear, before they are copied to the big job boards.

It starts with a focus on **Barcelona and Catalonia**, plus remote-friendly tech companies.

- **Seven ATS supported**: Greenhouse, Lever, Ashby, Workable, Recruitee, Personio, SmartRecruiters.
- **Search from the terminal** by keyword, city or remote.
- **Alerts only for new jobs** that match your profile, on Discord or Telegram, free on GitHub Actions.
- **A static website** with search and filters, rebuilt every day on GitHub Pages.
- **Self-checking list**: `jobradar check` (and CI) test every company so broken ones are caught.

## Quick start

```bash
pip install -e .
jobradar search "python" --remote
jobradar search --city barcelona
jobradar search "data" --city barcelona --level junior --level mid
```

Output looks like this (illustrative):

```
Typeform | Senior Backend Engineer | Barcelona, Spain | https://...
Wallapop | Data Engineer           | Barcelona        | https://...
```

## Website

```bash
jobradar export --out site   # writes site/index.html and site/jobs.json
```

A static page with search, city, company, level (intern, junior, mid, senior, lead, manager) and remote filters, no server needed. The
`Website` workflow rebuilds it every day and publishes it on GitHub Pages (enable it in
Settings, Pages, Source: GitHub Actions).

## Job alerts

```bash
cp profile.example.yaml profile.yaml        # keywords, cities, remote
jobradar update --profile profile.yaml --notify
```

`update` saves every job in a local SQLite file and reports only the ones not seen
before (the first run just saves a baseline). With `--notify` it posts them to Discord
and/or Telegram, configured with `DISCORD_WEBHOOK_URL`, `TELEGRAM_BOT_TOKEN` and
`TELEGRAM_CHAT_ID`. To run it daily for free, fork the repo, add those as repository
secrets, commit your `profile.yaml` and enable the `Job alerts` workflow.

## Add a company

The list is in [`companies.yaml`](companies.yaml). Adding one is a single line and
[CONTRIBUTING.md](CONTRIBUTING.md) explains how to find the right id. Not sure which ATS
a company uses? `jobradar find "Company name"` tries them all.

## Roadmap

- [x] Greenhouse, Lever and Ashby connectors, CLI
- [x] More ATS: Workable, Recruitee, Personio, SmartRecruiters
- [ ] Larger company list (Barcelona and Catalonia first, then Spain and Europe)
- [x] SQLite storage and "new since last run" detection
- [x] Alerts (Discord, Telegram) via GitHub Actions
- [ ] Email and RSS alerts
- [x] Static website on GitHub Pages
- [ ] Optional AI matching with your CV
- [ ] Publish on PyPI

## License

MIT
