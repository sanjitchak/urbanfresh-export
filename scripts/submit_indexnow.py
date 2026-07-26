#!/usr/bin/env python3
"""Submit the site's canonical sitemap URLs to the IndexNow API."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "urbanfreshrice.com"
DEFAULT_KEY = "ffd250145a6f352ff36e520b7d73038e"
DEFAULT_KEY_FILE = ROOT / f"{DEFAULT_KEY}.txt"
DEFAULT_KEY_LOCATION = f"https://{DEFAULT_HOST}/{DEFAULT_KEY}.txt"
DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
MAX_URLS = 10_000


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--sitemap", type=Path, default=ROOT / "sitemap.xml")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--key-location", default=DEFAULT_KEY_LOCATION)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--wait-for-key", action="store_true")
    parser.add_argument("--wait-timeout", type=int, default=300)
    parser.add_argument("--poll-interval", type=float, default=10)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def normalize_host(value: str) -> str:
    host = value.strip().casefold().rstrip(".")
    if not host or not re.fullmatch(r"[a-z0-9.-]+", host):
        raise RuntimeError(f"Invalid IndexNow host: {value!r}")
    if ".." in host or host.startswith(("-", ".")) or host.endswith("-"):
        raise RuntimeError(f"Invalid IndexNow host: {value!r}")
    return host


def read_key(path: Path) -> str:
    if not path.is_file():
        raise RuntimeError(f"IndexNow key file not found: {path}")
    key = path.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[A-Za-z0-9-]{8,128}", key):
        raise RuntimeError(f"IndexNow key file has an invalid value: {path}")
    return key


def validate_https_url(url: str, host: str, *, label: str) -> urllib.parse.SplitResult:
    parsed = urllib.parse.urlsplit(url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise RuntimeError(f"{label} has an invalid port: {url}") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname is None
        or normalize_host(parsed.hostname) != host
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.fragment
    ):
        raise RuntimeError(f"{label} must be an HTTPS URL on {host}: {url}")
    return parsed


def validate_key_location(key_location: str, host: str, key: str) -> None:
    parsed = validate_https_url(key_location, host, label="IndexNow key location")
    if parsed.query or parsed.path != f"/{key}.txt":
        raise RuntimeError(
            f"IndexNow key location must be the public root key file on {host}"
        )


def sitemap_urls(path: Path, host: str) -> list[str]:
    if not path.is_file():
        raise RuntimeError(f"Sitemap not found: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise RuntimeError(f"Invalid sitemap XML: {exc}") from exc
    if root.tag.rsplit("}", 1)[-1] != "urlset":
        raise RuntimeError("IndexNow submission requires a sitemap urlset")

    urls: list[str] = []
    seen: set[str] = set()
    for entry in root:
        if entry.tag.rsplit("}", 1)[-1] != "url":
            continue
        node = next(
            (
                child
                for child in entry
                if child.tag.rsplit("}", 1)[-1] == "loc"
            ),
            None,
        )
        if node is None:
            raise RuntimeError("Sitemap URL entry is missing its page location")
        url = (node.text or "").strip()
        parsed = validate_https_url(url, host, label="Sitemap URL")
        if parsed.query:
            raise RuntimeError(f"Sitemap URL must not contain a query string: {url}")
        if url not in seen:
            seen.add(url)
            urls.append(url)
    if not urls:
        raise RuntimeError("Sitemap contains no URLs")
    if len(urls) > MAX_URLS:
        raise RuntimeError(f"Sitemap contains more than {MAX_URLS} URLs")
    return urls


def fetch_live_key(key_location: str) -> str:
    separator = "&" if "?" in key_location else "?"
    cache_busted = f"{key_location}{separator}indexnow_check={int(time.time())}"
    request = urllib.request.Request(
        cache_busted,
        headers={"User-Agent": "UrbanFresh-Export-IndexNow-Submitter/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8").strip()
    except (UnicodeDecodeError, urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise RuntimeError("Could not verify the deployed IndexNow key file") from exc


def verify_live_key(key_location: str, key: str) -> None:
    if fetch_live_key(key_location) != key:
        raise RuntimeError("The deployed IndexNow key file does not match the local key")


def wait_for_live_key(
    key_location: str,
    key: str,
    *,
    timeout: int,
    poll_interval: float,
) -> None:
    deadline = time.monotonic() + max(timeout, 0)
    while True:
        try:
            verify_live_key(key_location, key)
            print("Verified the deployed IndexNow key file.")
            return
        except RuntimeError as exc:
            if time.monotonic() >= deadline:
                raise RuntimeError(
                    "Timed out waiting for the deployed IndexNow key file"
                ) from exc
        time.sleep(max(poll_interval, 0))


def submit_urls(
    endpoint: str,
    host: str,
    key: str,
    key_location: str,
    urls: list[str],
) -> int:
    parsed_endpoint = urllib.parse.urlsplit(endpoint)
    if parsed_endpoint.scheme != "https" or not parsed_endpoint.hostname:
        raise RuntimeError("IndexNow endpoint must be an HTTPS URL")
    body = json.dumps(
        {
            "host": host,
            "key": key,
            "keyLocation": key_location,
            "urlList": urls,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": "UrbanFresh-Export-IndexNow-Submitter/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            response.read()
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"IndexNow submission failed with HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Could not reach the IndexNow API") from exc
    if status not in {200, 202}:
        raise RuntimeError(f"IndexNow submission returned unexpected HTTP {status}")
    return status


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    host = normalize_host(args.host)
    key = read_key(args.key_file)
    validate_key_location(args.key_location, host, key)
    urls = sitemap_urls(args.sitemap, host)

    if args.dry_run:
        print(f"DRY RUN: validated {len(urls)} IndexNow URL(s) for {host}.")
        return 0

    if args.wait_for_key:
        wait_for_live_key(
            args.key_location,
            key,
            timeout=args.wait_timeout,
            poll_interval=args.poll_interval,
        )
    else:
        verify_live_key(args.key_location, key)
        print("Verified the deployed IndexNow key file.")

    status = submit_urls(args.endpoint, host, key, args.key_location, urls)
    print(f"Submitted {len(urls)} URL(s) to IndexNow (HTTP {status}).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
