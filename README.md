# JobRadar

Search job openings straight from company career pages, using the public APIs of
applicant tracking systems (Greenhouse, Lever, Ashby). No API keys, no scraping of
job boards, no blocks.

> Early work in progress. See the roadmap below.

## Quick start

```bash
pip install -e ".[dev]"
jobradar search "python" --remote
```

Companies live in [`companies.yaml`](companies.yaml). Adding one is a one-line pull request.

## Roadmap

- [x] Greenhouse, Lever and Ashby connectors, CLI
- [ ] More ATS: Workable, Recruitee, Personio, SmartRecruiters
- [ ] Larger company list (Spain and Europe first)
- [ ] SQLite storage and "new since last run" detection
- [ ] Alerts (Telegram, Discord, email, RSS) via GitHub Actions
- [ ] Static website on GitHub Pages
- [ ] Optional AI matching with your CV

## License

MIT
