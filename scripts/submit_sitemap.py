#!/usr/bin/env python3
"""Submit the deployed UrbanFresh Export sitemap to Google Search Console."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from seo_improver import (
    GSC_API,
    GSC_WRITE_SCOPE,
    gsc_request,
    load_dotenv,
    service_account_token,
    verify_property,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROPERTY = "sc-domain:urbanfreshrice.com"
DEFAULT_SITEMAP_URL = "https://urbanfreshrice.com/sitemap.xml"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-property", default=DEFAULT_PROPERTY)
    parser.add_argument("--sitemap-url", default=DEFAULT_SITEMAP_URL)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env.local")
    parser.add_argument("--local-sitemap", type=Path, default=ROOT / "sitemap.xml")
    parser.add_argument("--wait-for-live", action="store_true")
    parser.add_argument("--wait-timeout", type=int, default=300)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_live_sitemap(url: str) -> bytes:
    separator = "&" if "?" in url else "?"
    cache_busted = f"{url}{separator}deploy_check={int(time.time())}"
    request = urllib.request.Request(
        cache_busted,
        headers={"User-Agent": "UrbanFresh-Export-Search-Console-Submitter/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Live sitemap returned HTTP {exc.code}: {url}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not fetch live sitemap {url}: {exc.reason}") from exc


def wait_for_live_sitemap(local_path: Path, sitemap_url: str, timeout: int) -> None:
    if not local_path.exists():
        raise RuntimeError(f"Local sitemap not found: {local_path}")
    local_bytes = local_path.read_bytes()
    local_hash = sha256(local_bytes)
    deadline = time.monotonic() + max(timeout, 0)
    last_hash = "unavailable"

    while True:
        try:
            live_bytes = fetch_live_sitemap(sitemap_url)
            last_hash = sha256(live_bytes)
            if live_bytes == local_bytes:
                print(f"Verified live sitemap matches the deployed repository file ({local_hash[:12]}).")
                return
        except RuntimeError:
            last_hash = "unavailable"

        if time.monotonic() >= deadline:
            raise RuntimeError(
                "Timed out waiting for the live sitemap to match the repository file "
                f"(local {local_hash[:12]}, live {last_hash[:12]})."
            )
        time.sleep(10)


def property_permission(token: str, site_property: str) -> str:
    entries = gsc_request(token, "/sites").get("siteEntry", [])
    for entry in entries:
        if entry.get("siteUrl") == site_property:
            return str(entry.get("permissionLevel", "unknown"))
    return "not-visible"


def submit_sitemap(token: str, site_property: str, sitemap_url: str) -> None:
    encoded_property = urllib.parse.quote(site_property, safe="")
    encoded_sitemap = urllib.parse.quote(sitemap_url, safe="")
    endpoint = f"{GSC_API}/sites/{encoded_property}/sitemaps/{encoded_sitemap}"
    request = urllib.request.Request(
        endpoint,
        headers={"Authorization": f"Bearer {token}"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            response.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            parsed: dict[str, Any] = json.loads(detail)
            detail = str(parsed.get("error", {}).get("message", detail))
        except json.JSONDecodeError:
            pass
        raise RuntimeError(f"Search Console sitemap submission failed (HTTP {exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach Search Console sitemap API: {exc.reason}") from exc


def verify_sitemap(token: str, site_property: str, sitemap_url: str) -> dict[str, Any]:
    encoded_property = urllib.parse.quote(site_property, safe="")
    response = gsc_request(token, f"/sites/{encoded_property}/sitemaps")
    for sitemap in response.get("sitemap", []):
        if sitemap.get("path") == sitemap_url:
            return sitemap
    raise RuntimeError(f"Search Console did not list the submitted sitemap: {sitemap_url}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.wait_for_live:
        wait_for_live_sitemap(args.local_sitemap, args.sitemap_url, args.wait_timeout)

    if args.dry_run:
        print(f"DRY RUN: would submit {args.sitemap_url} for {args.site_property}.")
        return 0

    load_dotenv(args.env_file)
    credentials_json = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
    if not credentials_json:
        raise RuntimeError(
            "GSC_CREDENTIALS_JSON is not configured. Set it locally or as a GitHub Actions secret."
        )

    token = service_account_token(credentials_json, scope=GSC_WRITE_SCOPE)
    verify_property(token, args.site_property)
    permission = property_permission(token, args.site_property)
    print(f"Verified Search Console property access ({permission}).")

    if not args.verify_only:
        submit_sitemap(token, args.site_property, args.sitemap_url)
        print(f"Submitted {args.sitemap_url} to {args.site_property}.")

    if args.verify or args.verify_only:
        sitemap = verify_sitemap(token, args.site_property, args.sitemap_url)
        last_submitted = sitemap.get("lastSubmitted", "recorded")
        print(f"Verified Search Console sitemap record (last submitted: {last_submitted}).")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
