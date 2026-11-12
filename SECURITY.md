# Security policy

## Supported versions

Only the latest release and the `main` branch get security fixes.

## Reporting a vulnerability

Please do **not** open a public issue. Report it privately through
[GitHub security advisories](https://github.com/dabupr/JobRadar/security/advisories/new).

You will get an answer within 7 days. Once a fix is released you will be credited in the
release notes, unless you prefer to stay anonymous.

## Scope

JobRadar only reads public job APIs and stores data locally or in GitHub Actions caches.
Secrets (Discord webhook, Telegram token) are read from environment variables and are never
written to logs or to the website. Reports about leaking them are especially welcome.
