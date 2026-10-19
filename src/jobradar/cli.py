from __future__ import annotations

import argparse
import sys

import httpx

from jobradar.companies import load_companies
from jobradar.connectors import CONNECTORS


def collect(companies: list[dict], client: httpx.Client) -> list:
    jobs = []
    for company in companies:
        fetch = CONNECTORS.get(company["ats"])
        if fetch is None:
            print(f"warning: unknown ATS {company['ats']!r} for {company['name']}", file=sys.stderr)
            continue
        try:
            jobs.extend(fetch(company["slug"], company["name"], client))
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            print(f"warning: {company['name']}: {exc}", file=sys.stderr)
    return jobs


def run_check(companies: list[dict]) -> int:
    failed = 0
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for company in companies:
            fetch = CONNECTORS.get(company["ats"])
            try:
                count = len(fetch(company["slug"], company["name"], client)) if fetch else None
                status = "UNKNOWN ATS" if count is None else f"ok ({count} jobs)"
            except (httpx.HTTPError, ValueError, KeyError) as exc:
                count, status = None, f"FAIL {exc}"
            if count is None:
                failed += 1
            print(f"{company['name']} [{company['ats']}/{company['slug']}]: {status}")
    print(f"{len(companies) - failed}/{len(companies)} companies ok", file=sys.stderr)
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobradar", description="Search company career pages.")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="search jobs across the listed companies")
    search.add_argument("query", nargs="?", default=None)
    search.add_argument("--remote", action="store_true", help="only remote jobs")
    search.add_argument("--city", default=None, help="only jobs whose location contains this")
    search.add_argument("--companies", default="companies.yaml", help="path to companies file")
    check = sub.add_parser("check", help="check that every company in the list still works")
    check.add_argument("--companies", default="companies.yaml", help="path to companies file")
    args = parser.parse_args(argv)

    if args.command == "check":
        return run_check(load_companies(args.companies))

    companies = load_companies(args.companies)
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        jobs = collect(companies, client)
    found = [job for job in jobs if job.matches(args.query, args.remote, args.city)]
    for job in found:
        print(f"{job.company} | {job.title} | {job.location} | {job.url}")
    print(f"{len(found)} jobs", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
