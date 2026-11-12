# JobRadar

[![CI](https://github.com/dabupr/JobRadar/actions/workflows/ci.yml/badge.svg)](https://github.com/dabupr/JobRadar/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Job alerts straight from company career pages. No scraping of job boards, no API keys, no blocks.**

Most companies publish their openings through an applicant tracking system (ATS) such as
Greenhouse, Lever or Ashby, and those systems have public APIs. JobRadar reads them
directly for a list of companies you can extend with a one-line pull request, so you see
new jobs the day they appear, before they are copied to the big job boards.

It starts with a focus on **Barcelona and Catalonia**, plus remote-friendly tech companies.

**[Browse the jobs online](https://dabupr.github.io/JobRadar/)**, no install needed. It is rebuilt every day.

- **300+ companies and 10 ATS**: Greenhouse, Lever, Ashby, Workable, Recruitee, Personio,
  SmartRecruiters, Teamtailor, BambooHR and Breezy, plus the open remote boards Remote OK,
  Remotive, Arbeitnow and We Work Remotely.
- **Search from the terminal** by keyword, city or remote.
- **Alerts only for new jobs** that match your profile, on Discord or Telegram, free on GitHub Actions.
- **A static website** with search, filters, newest-first sorting and saved jobs, rebuilt every day on GitHub Pages.
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

A static page, no server needed, with:

- search by keyword, city (with aliases such as BCN), company, level (intern, junior, mid,
  senior, lead, manager) and remote;
- newest jobs first, a *New* badge for the last few days and a "posted in the last day, 3 days,
  week or month" filter;
- a star to save jobs in your browser and a "Saved only" view;
- filters kept in the address, so a search such as
  [Barcelona, junior](https://dabupr.github.io/JobRadar/#city=barcelona&level=junior) can be shared as a link.

The
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
- [x] More ATS: Workable, Recruitee, Personio, SmartRecruiters, Teamtailor, BambooHR, Breezy
- [x] Open remote job boards (Remote OK, Remotive, Arbeitnow, We Work Remotely)
- [x] Seniority levels guessed from the title
- [ ] Larger company list (300+ today; more of Spain and Europe)
- [ ] Workday and Hacker News "Who is hiring"
- [x] SQLite storage and "new since last run" detection
- [x] Alerts (Discord, Telegram) via GitHub Actions
- [ ] Email and RSS alerts
- [x] Static website on GitHub Pages
- [ ] Optional AI matching with your CV
- [ ] Publish on PyPI

## License

MIT

## Safety and limits

- Everything runs on public data: no logins, no API keys. Alert tokens live in GitHub Secrets and never appear in the code or in error messages.
- Every request identifies itself (`JobRadar/<version>`), has a 20 s timeout and the workflows have a time limit and read-only permissions.
- The alert workflow never overlaps with itself and sends at most 10 messages per run, so a first import cannot flood Discord or Telegram.
- On a public repository GitHub Actions and GitHub Pages are free. Pages allows a 1 GB site and about 100 GB of traffic per month; the whole site is a few MB.
