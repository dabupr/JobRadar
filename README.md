# JobRadar

Search job openings straight from company career pages, using the public APIs of
applicant tracking systems (Greenhouse, Lever, Ashby). No API keys, no scraping of
job boards, no blocks.

> Early work in progress. See the roadmap below.

## Quick start

```bash
pip install -e ".[dev]"
jobradar search "python" --remote
jobradar search --city barcelona
jobradar check   # verify every company in companies.yaml still works
```

Companies live in [`companies.yaml`](companies.yaml). Adding one is a one-line pull request.

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

## Roadmap

- [x] Greenhouse, Lever and Ashby connectors, CLI
- [x] More ATS: Workable, Recruitee, Personio, SmartRecruiters
- [ ] Larger company list (Barcelona and Catalonia first, then Spain and Europe)
- [x] SQLite storage and "new since last run" detection
- [x] Alerts (Discord, Telegram) via GitHub Actions
- [ ] Email and RSS alerts
- [ ] Static website on GitHub Pages
- [ ] Optional AI matching with your CV

## License

MIT
