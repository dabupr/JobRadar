from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import httpx

from jobradar.companies import load_companies, load_feeds
from jobradar.connectors import CONNECTORS
from jobradar.feeds import FEEDS
from jobradar.notify import notify
from jobradar.places import open_to_spain
from jobradar.profile import Profile, load_profile
from jobradar.seniority import LEVELS
from jobradar.site import write_site
from jobradar.storage import Store

FETCH_ERRORS = (httpx.HTTPError, ValueError, KeyError, ET.ParseError)


def collect(path: str, client: httpx.Client) -> list:
    """Fetch every company listed in the file, plus the open job feeds it enables."""
    jobs = []
    for company in load_companies(path):
        fetch = CONNECTORS.get(company["ats"])
        if fetch is None:
            print(f"warning: unknown ATS {company['ats']!r} for {company['name']}", file=sys.stderr)
            continue
        try:
            jobs.extend(fetch(company["slug"], company["name"], client))
        except FETCH_ERRORS as exc:
            print(f"warning: {company['name']}: {exc}", file=sys.stderr)
    for feed in load_feeds(path):
        fetch_feed = FEEDS.get(feed)
        if fetch_feed is None:
            print(f"warning: unknown feed {feed!r}", file=sys.stderr)
            continue
        try:
            jobs.extend(fetch_feed(client))
        except FETCH_ERRORS as exc:
            print(f"warning: feed {feed}: {exc}", file=sys.stderr)
    return jobs


def run_check(companies: list[dict], feeds: list[str]) -> int:
    failed = 0
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        for company in companies:
            fetch = CONNECTORS.get(company["ats"])
            try:
                count = len(fetch(company["slug"], company["name"], client)) if fetch else None
                status = "UNKNOWN ATS" if count is None else f"ok ({count} jobs)"
            except FETCH_ERRORS as exc:
                count, status = None, f"FAIL {exc}"
            if count is None:
                failed += 1
            print(f"{company['name']} [{company['ats']}/{company['slug']}]: {status}")
        for feed in feeds:
            fetch_feed = FEEDS.get(feed)
            try:
                count = len(fetch_feed(client)) if fetch_feed else None
                status = "UNKNOWN FEED" if count is None else f"ok ({count} jobs)"
            except FETCH_ERRORS as exc:
                count, status = None, f"FAIL {exc}"
            if count is None:
                failed += 1
            print(f"feed {feed}: {status}")
    total = len(companies) + len(feeds)
    print(f"{total - failed}/{total} sources ok", file=sys.stderr)
    return 1 if failed else 0


def run_update(args: argparse.Namespace) -> int:
    profile = load_profile(args.profile) if args.profile else Profile()
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        jobs = collect(args.companies, client)
        store = Store(args.db)
        first_run = store.is_empty()
        new = [job for job in store.upsert(jobs) if profile.accepts(job)]
        store.close()
        if first_run:
            print(f"first run: saved {len(jobs)} jobs as baseline, no alerts sent", file=sys.stderr)
            return 0
        for job in new:
            print(f"NEW {job.company} | {job.title} | {job.location} | {job.url}")
        print(f"{len(new)} new jobs", file=sys.stderr)
        if new and args.notify:
            channels = notify(new, client)
            print(f"notified: {', '.join(channels) or 'no channel configured'}", file=sys.stderr)
    return 0


def slug_variants(name: str) -> list[str]:
    plain = "".join(c for c in name.lower() if c.isalnum() or c == " ")
    base = plain.replace(" ", "")
    variants = [base, plain.replace(" ", "-"), base + "app", base + "hq", base + "careers"]
    variants.append(base.capitalize())  # SmartRecruiters ids are case sensitive
    return list(dict.fromkeys(variants))


def find_name(name: str, client: httpx.Client) -> list[str]:
    hits = []
    for slug in slug_variants(name):
        for ats, fetch in CONNECTORS.items():
            if slug != slug.lower() and ats != "smartrecruiters":
                continue
            try:
                count = len(fetch(slug, name, client))
            except FETCH_ERRORS:
                continue
            if count == 0:
                continue  # SmartRecruiters answers 200 with no jobs for any id
            hits.append(f"  - {{ name: {name}, ats: {ats}, slug: {slug} }}  # {count} jobs")
    return hits


def run_find(names: list[str]) -> int:
    with httpx.Client(timeout=20, follow_redirects=True) as client, ThreadPoolExecutor(8) as pool:
        results = list(pool.map(lambda n: find_name(n, client), names))
    for name, hits in zip(names, results):
        for hit in hits:
            print(hit)
    missing = [name for name, hits in zip(names, results) if not hits]
    print(f"no match for {len(missing)} of {len(names)}: {', '.join(missing)}", file=sys.stderr)
    return 0


def run_stats(args: argparse.Namespace) -> int:
    with httpx.Client(timeout=20, follow_redirects=True) as client:
        jobs = collect(args.companies, client)
    plain = [j for j in jobs if args.city.lower() in j.location.lower()]
    smart = [j for j in jobs if j.matches(city=args.city)]
    spain = [j for j in jobs if j.matches(city=args.city) or open_to_spain(j.location, j.remote)]
    print(f"total jobs: {len(jobs)}")
    print(f"{args.city}, plain substring match: {len(plain)}")
    print(f"{args.city}, with aliases: {len(smart)}")
    print(f"{args.city}, with aliases + remote open to Spain/Europe: {len(spain)}")
    per_company = Counter(j.company for j in smart)
    for company, count in per_company.most_common():
        print(f"  {company}: {count}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jobradar", description="Search company career pages.")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="search jobs across the listed companies")
    search.add_argument("query", nargs="?", default=None)
    search.add_argument("--remote", action="store_true", help="only remote jobs")
    search.add_argument("--city", default=None, help="only jobs whose location contains this")
    search.add_argument(
        "--level", action="append", choices=LEVELS,
        help="only this seniority, guessed from the title (repeat for several)",
    )
    search.add_argument("--companies", default="companies.yaml", help="path to companies file")
    check = sub.add_parser("check", help="check that every company in the list still works")
    check.add_argument("--companies", default="companies.yaml", help="path to companies file")
    update = sub.add_parser("update", help="save jobs and report the ones not seen before")
    update.add_argument("--companies", default="companies.yaml", help="path to companies file")
    update.add_argument("--profile", default=None, help="profile.yaml to filter new jobs")
    update.add_argument("--db", default="jobradar.sqlite", help="SQLite file with seen jobs")
    update.add_argument("--notify", action="store_true", help="send new jobs to Discord/Telegram")
    export = sub.add_parser("export", help="write a static website with every job")
    export.add_argument("--companies", default="companies.yaml", help="path to companies file")
    export.add_argument("--out", default="site", help="output directory")
    stats = sub.add_parser("stats", help="count jobs in a city, per company")
    stats.add_argument("--city", default="barcelona")
    stats.add_argument("--companies", default="companies.yaml", help="path to companies file")
    find = sub.add_parser("find", help="guess the ATS and slug of companies by name")
    find.add_argument("names", nargs="+", help="company names")
    args = parser.parse_args(argv)

    if args.command == "export":
        with httpx.Client(timeout=20, follow_redirects=True) as client:
            jobs = collect(args.companies, client)
        write_site(jobs, args.out)
        print(f"wrote {len(jobs)} jobs to {args.out}/", file=sys.stderr)
        return 0
    if args.command == "update":
        return run_update(args)
    if args.command == "stats":
        return run_stats(args)
    if args.command == "find":
        return run_find(args.names)
    if args.command == "check":
        return run_check(load_companies(args.companies), load_feeds(args.companies))

    with httpx.Client(timeout=20, follow_redirects=True) as client:
        jobs = collect(args.companies, client)
    found = [job for job in jobs if job.matches(args.query, args.remote, args.city, args.level)]
    for job in found:
        print(f"{job.company} | {job.title} | {job.location} | {job.url}")
    print(f"{len(found)} jobs", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
