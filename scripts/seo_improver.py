#!/usr/bin/env python3
"""Free, local SEO improvement loop for the UrbanFresh Export website.

The script uses only Python's standard library and the system OpenSSL binary.
It can read Google Search Console directly through a read-only service account,
or process two CSV exports when API credentials are not available.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROPERTY = "sc-domain:urbanfreshrice.com"
DEFAULT_DOMAIN = "urbanfreshrice.com"
TOKEN_URL = "https://oauth2.googleapis.com/token"
GSC_SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
GSC_WRITE_SCOPE = "https://www.googleapis.com/auth/webmasters"
GSC_API = "https://searchconsole.googleapis.com/webmasters/v3"
REPORT_FIELDS = [
    "keyword",
    "ranking_url",
    "clicks",
    "previous_clicks",
    "clicks_delta",
    "impressions",
    "previous_impressions",
    "ctr",
    "previous_ctr",
    "average_position",
    "previous_position",
    "position_delta",
    "status",
]
MARKET_FIELDS = [
    "country",
    "device",
    "clicks",
    "previous_clicks",
    "clicks_delta",
    "impressions",
    "previous_impressions",
    "impressions_delta",
    "ctr",
    "previous_ctr",
    "average_position",
    "previous_position",
    "position_delta",
]
MIN_ACTION_IMPRESSIONS = 100
MIN_CANNIBAL_IMPRESSIONS = 50


@dataclass
class Metric:
    query: str
    page: str = ""
    clicks: float = 0.0
    impressions: float = 0.0
    ctr: float = 0.0
    position: float | None = None
    device: str = ""
    country: str = ""

    @property
    def key(self) -> tuple[str, str]:
        return (self.query.casefold().strip(), self.page.strip())


@dataclass
class MarketMetric:
    country: str
    device: str
    clicks: float = 0.0
    impressions: float = 0.0
    ctr: float = 0.0
    position: float | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.country.casefold().strip(), self.device.casefold().strip())


@dataclass
class Opportunity:
    kind: str
    issue_id: str
    score: float
    query: str
    page: str
    evidence: str
    action: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the free local UrbanFresh Export weekly SEO improvement loop."
    )
    parser.add_argument("--site-property", default=DEFAULT_PROPERTY)
    parser.add_argument("--domain", default=DEFAULT_DOMAIN)
    parser.add_argument("--current-csv", type=Path)
    parser.add_argument("--previous-csv", type=Path)
    parser.add_argument("--report-date", type=dt.date.fromisoformat, default=dt.date.today())
    parser.add_argument("--output-root", type=Path, default=ROOT / "reports" / "seo-improver")
    parser.add_argument("--skip-audit", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args(argv)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if stripped.startswith("{"):
        try:
            credentials = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Invalid raw service-account JSON in {path}: {exc}") from exc
        if credentials.get("type") != "service_account":
            raise RuntimeError(f"Raw JSON in {path} is not a Google service-account key")
        os.environ.setdefault(
            "GSC_CREDENTIALS_JSON",
            json.dumps(credentials, separators=(",", ":")),
        )
        return

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def http_date_epoch(value: str) -> int:
    parsed = parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return int(parsed.timestamp())


def google_server_epoch() -> int:
    """Use Google's clock so JWT auth survives a locally skewed Mac clock."""
    request = urllib.request.Request(TOKEN_URL, method="HEAD")
    headers = None
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            headers = response.headers
    except urllib.error.HTTPError as exc:
        # The token endpoint returns 404 to HEAD but still supplies an authoritative Date header.
        headers = exc.headers
    except urllib.error.URLError:
        pass
    date_header = headers.get("Date") if headers is not None else None
    if date_header:
        return http_date_epoch(date_header)
    return int(dt.datetime.now(dt.timezone.utc).timestamp())


def service_account_token(credentials_json: str, scope: str = GSC_SCOPE) -> str:
    try:
        credentials = json.loads(credentials_json)
        client_email = credentials["client_email"]
        private_key = credentials["private_key"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise RuntimeError(f"Invalid GSC_CREDENTIALS_JSON: {exc}") from exc

    now = google_server_epoch()
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}, separators=(",", ":")).encode())
    claim = b64url(
        json.dumps(
            {
                "iss": client_email,
                "scope": scope,
                "aud": TOKEN_URL,
                "iat": now,
                "exp": now + 3600,
            },
            separators=(",", ":"),
        ).encode()
    )
    signing_input = f"{header}.{claim}".encode("ascii")

    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".pem") as key_file:
            key_file.write(private_key)
            key_file.flush()
            signed = subprocess.run(
                ["openssl", "dgst", "-sha256", "-sign", key_file.name],
                input=signing_input,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
    except FileNotFoundError as exc:
        raise RuntimeError("OpenSSL is required but was not found on PATH") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Could not sign the Google service-account JWT: {message}") from exc

    assertion = f"{header}.{claim}.{b64url(signed.stdout)}"
    body = urllib.parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    response = request_json(request)
    token = response.get("access_token")
    if not token:
        raise RuntimeError("Google token exchange returned no access_token")
    return str(token)


def request_json(request: urllib.request.Request) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {request.full_url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach {request.full_url}: {exc.reason}") from exc


def gsc_request(token: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        f"{GSC_API}{path}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    return request_json(request)


def verify_property(token: str, site_property: str) -> None:
    sites = gsc_request(token, "/sites").get("siteEntry", [])
    matching = [site for site in sites if site.get("siteUrl") == site_property]
    if not matching:
        visible = ", ".join(str(site.get("siteUrl", "")) for site in sites) or "none"
        raise RuntimeError(
            f"{site_property} is not visible to the service account. Visible properties: {visible}"
        )
    permission = str(matching[0].get("permissionLevel", ""))
    if permission in {"", "siteUnverifiedUser"}:
        raise RuntimeError(f"{site_property} has unusable permission level: {permission or 'missing'}")


def query_gsc_period(token: str, site_property: str, start: dt.date, end: dt.date) -> list[Metric]:
    rows: list[Metric] = []
    start_row = 0
    row_limit = 25_000
    encoded_property = urllib.parse.quote(site_property, safe="")
    while True:
        payload = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["query", "page", "device", "country"],
            "type": "web",
            "dataState": "final",
            "rowLimit": row_limit,
            "startRow": start_row,
        }
        data = gsc_request(
            token,
            f"/sites/{encoded_property}/searchAnalytics/query",
            payload,
        )
        batch = data.get("rows", [])
        for row in batch:
            keys = row.get("keys", [])
            rows.append(
                Metric(
                    query=str(keys[0]) if keys else "",
                    page=str(keys[1]) if len(keys) > 1 else "",
                    clicks=float(row.get("clicks", 0)),
                    impressions=float(row.get("impressions", 0)),
                    ctr=float(row.get("ctr", 0)),
                    position=float(row["position"]) if row.get("position") is not None else None,
                    device=str(keys[2]) if len(keys) > 2 else "",
                    country=str(keys[3]) if len(keys) > 3 else "",
                )
            )
        if len(batch) < row_limit:
            break
        start_row += row_limit
    return rows


def normalized_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")


def parse_number(value: str | None, *, percent: bool = False) -> float:
    text = str(value or "").strip().replace(",", "")
    if not text:
        return 0.0
    is_percent = text.endswith("%")
    if is_percent:
        text = text[:-1]
    number = float(text)
    if is_percent or percent:
        number /= 100.0
    return number


def load_search_console_csv(path: Path) -> list[Metric]:
    if not path.exists():
        raise RuntimeError(f"Search Console CSV not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise RuntimeError(f"Search Console CSV has no header: {path}")
        aliases = {normalized_header(name): name for name in reader.fieldnames}

        def column(*names: str) -> str | None:
            for name in names:
                if name in aliases:
                    return aliases[name]
            return None

        query_col = column("query", "top_queries", "keyword")
        page_col = column("page", "top_pages", "ranking_url", "url")
        clicks_col = column("clicks")
        impressions_col = column("impressions")
        ctr_col = column("ctr", "average_ctr")
        position_col = column("position", "average_position")
        device_col = column("device")
        country_col = column("country")
        if not query_col or not impressions_col or not position_col:
            raise RuntimeError(
                "CSV needs Query (or Top queries), Impressions, and Position columns"
            )

        rows: list[Metric] = []
        for item in reader:
            query = str(item.get(query_col, "")).strip()
            if not query:
                continue
            impressions = parse_number(item.get(impressions_col))
            clicks = parse_number(item.get(clicks_col)) if clicks_col else 0.0
            ctr = parse_number(item.get(ctr_col)) if ctr_col else (
                clicks / impressions if impressions else 0.0
            )
            rows.append(
                Metric(
                    query=query,
                    page=str(item.get(page_col, "")).strip() if page_col else "",
                    clicks=clicks,
                    impressions=impressions,
                    ctr=ctr,
                    position=parse_number(item.get(position_col)),
                    device=str(item.get(device_col, "")).strip() if device_col else "",
                    country=str(item.get(country_col, "")).strip() if country_col else "",
                )
            )
    return rows


def aggregate_metrics(rows: Iterable[Metric]) -> list[Metric]:
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not row.query.strip():
            continue
        bucket = buckets.setdefault(
            row.key,
            {
                "query": row.query.strip(),
                "page": row.page.strip(),
                "clicks": 0.0,
                "impressions": 0.0,
                "position_weight": 0.0,
                "position_impressions": 0.0,
            },
        )
        bucket["clicks"] += row.clicks
        bucket["impressions"] += row.impressions
        if row.position is not None:
            weight = max(row.impressions, 1.0)
            bucket["position_weight"] += row.position * weight
            bucket["position_impressions"] += weight

    result: list[Metric] = []
    for bucket in buckets.values():
        impressions = float(bucket["impressions"])
        position_weight = float(bucket["position_impressions"])
        result.append(
            Metric(
                query=str(bucket["query"]),
                page=str(bucket["page"]),
                clicks=float(bucket["clicks"]),
                impressions=impressions,
                ctr=float(bucket["clicks"]) / impressions if impressions else 0.0,
                position=(
                    float(bucket["position_weight"]) / position_weight
                    if position_weight
                    else None
                ),
            )
        )
    return sorted(result, key=lambda row: (-row.impressions, row.query.casefold(), row.page))


def aggregate_market_metrics(rows: Iterable[Metric]) -> list[MarketMetric]:
    buckets: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        country = row.country.strip().casefold() or "unknown"
        device = row.device.strip().upper() or "UNKNOWN"
        bucket = buckets.setdefault(
            (country, device),
            {
                "clicks": 0.0,
                "impressions": 0.0,
                "position_weight": 0.0,
                "position_impressions": 0.0,
            },
        )
        bucket["clicks"] += row.clicks
        bucket["impressions"] += row.impressions
        if row.position is not None:
            weight = max(row.impressions, 1.0)
            bucket["position_weight"] += row.position * weight
            bucket["position_impressions"] += weight

    result: list[MarketMetric] = []
    for (country, device), bucket in buckets.items():
        impressions = float(bucket["impressions"])
        position_impressions = float(bucket["position_impressions"])
        result.append(
            MarketMetric(
                country=country,
                device=device,
                clicks=float(bucket["clicks"]),
                impressions=impressions,
                ctr=float(bucket["clicks"]) / impressions if impressions else 0.0,
                position=(
                    float(bucket["position_weight"]) / position_impressions
                    if position_impressions
                    else None
                ),
            )
        )
    return sorted(result, key=lambda row: (-row.impressions, row.country, row.device))


def build_market_snapshot(
    current: list[MarketMetric], previous: list[MarketMetric]
) -> list[dict[str, Any]]:
    current_by_key = {row.key: row for row in current}
    previous_by_key = {row.key: row for row in previous}
    result: list[dict[str, Any]] = []
    for key in set(current_by_key) | set(previous_by_key):
        now = current_by_key.get(key)
        before = previous_by_key.get(key)
        row = now or before
        assert row is not None
        position_delta = (
            before.position - now.position
            if now and before and now.position is not None and before.position is not None
            else None
        )
        result.append(
            {
                "country": row.country,
                "device": row.device,
                "clicks": round(now.clicks, 2) if now else 0,
                "previous_clicks": round(before.clicks, 2) if before else "",
                "clicks_delta": round(now.clicks - before.clicks, 2) if now and before else "",
                "impressions": round(now.impressions, 2) if now else 0,
                "previous_impressions": round(before.impressions, 2) if before else "",
                "impressions_delta": (
                    round(now.impressions - before.impressions, 2) if now and before else ""
                ),
                "ctr": round(now.ctr, 6) if now else 0,
                "previous_ctr": round(before.ctr, 6) if before else "",
                "average_position": (
                    round(now.position, 2) if now and now.position is not None else ""
                ),
                "previous_position": (
                    round(before.position, 2) if before and before.position is not None else ""
                ),
                "position_delta": round(position_delta, 2) if position_delta is not None else "",
            }
        )
    return sorted(
        result,
        key=lambda row: (-float(row["impressions"]), str(row["country"]), str(row["device"])),
    )


def tracked_keywords() -> list[str]:
    path = ROOT / "seo" / "keyword-map.csv"
    values: list[str] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            intent = str(row.get("primary_search_intent", ""))
            for keyword in re.split(r"\s*/\s*", intent):
                keyword = keyword.strip()
                if keyword and keyword.casefold() not in {value.casefold() for value in values}:
                    values.append(keyword)
    return values


def local_path_from_url(url: str, domain: str) -> Path | None:
    if not url:
        return None
    parsed = urllib.parse.urlsplit(url)
    if parsed.netloc and parsed.netloc.casefold().removeprefix("www.") != domain.casefold().removeprefix("www."):
        return None
    relative = parsed.path.lstrip("/") or "index.html"
    path = (ROOT / relative).resolve()
    return path if ROOT in path.parents and path.exists() else None


def html_metadata(url: str, domain: str) -> tuple[str, str]:
    path = local_path_from_url(url, domain)
    if not path:
        return ("", "")
    html = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.I | re.S)
    description_match = re.search(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        html,
        flags=re.I | re.S,
    )
    title = unescape(re.sub(r"\s+", " ", title_match.group(1)).strip()) if title_match else ""
    description = unescape(re.sub(r"\s+", " ", description_match.group(1)).strip()) if description_match else ""
    return title, description


def title_case_keyword(keyword: str) -> str:
    small = {"a", "an", "and", "for", "in", "of", "the", "to"}
    words = keyword.split()
    return " ".join(
        word if index and word.casefold() in small else word[:1].upper() + word[1:]
        for index, word in enumerate(words)
    )


def suggested_title(keyword: str) -> str:
    candidate = f"{title_case_keyword(keyword)} | UrbanFresh"
    if len(candidate) < 30:
        candidate = f"{title_case_keyword(keyword)} | Bulk Quote | UrbanFresh"
    if len(candidate) > 65:
        candidate = f"{title_case_keyword(keyword)[:48].rstrip()} | UrbanFresh"
    return candidate


def expected_ctr(position: float | None) -> float:
    if position is None:
        return 0.0
    if position <= 3:
        return 0.08
    if position <= 10:
        return 0.03
    if position <= 20:
        return 0.015
    return 0.01


def detect_opportunities(
    current: list[Metric], previous: list[Metric], domain: str
) -> list[Opportunity]:
    previous_by_key = {row.key: row for row in previous}
    opportunities: list[Opportunity] = []
    counters: defaultdict[str, int] = defaultdict(int)

    def next_id(kind: str) -> str:
        counters[kind] += 1
        return f"SEO-{kind}-{counters[kind]:03d}"

    for row in current:
        if not row.page or row.position is None:
            continue
        if 4 <= row.position <= 20 and row.impressions >= MIN_ACTION_IMPRESSIONS:
            opportunities.append(
                Opportunity(
                    kind="STRIKE",
                    issue_id=next_id("STRIKE"),
                    score=row.impressions * (21 - row.position) / 20,
                    query=row.query,
                    page=row.page,
                    evidence=(
                        f"{int(row.impressions)} impressions at average position {row.position:.1f} "
                        f"with {int(row.clicks)} clicks."
                    ),
                    action=(
                        f"Add a focused buyer-answer section for ‘{row.query}’ on this page, covering "
                        "variety, processing, order quantity, packaging and destination; add two relevant "
                        "internal links to the page and keep the quote CTA immediately after the section."
                    ),
                )
            )

        target_ctr = expected_ctr(row.position)
        if row.impressions >= MIN_ACTION_IMPRESSIONS and row.ctr < target_ctr:
            current_title, _ = html_metadata(row.page, domain)
            new_title = suggested_title(row.query)
            opportunities.append(
                Opportunity(
                    kind="CTR",
                    issue_id=next_id("CTR"),
                    score=row.impressions * (target_ctr - row.ctr) * 100,
                    query=row.query,
                    page=row.page,
                    evidence=(
                        f"{int(row.impressions)} impressions, {row.ctr:.1%} CTR and average position "
                        f"{row.position:.1f}; the local benchmark for this position band is {target_ctr:.1%}."
                    ),
                    action=(
                        f"Test the title “{new_title}” instead of “{current_title or 'the current title'}”. "
                        "Keep the existing description unless Search Console shows the title test alone did not improve CTR."
                    ),
                )
            )

        prior = previous_by_key.get(row.key)
        if prior and prior.position is not None:
            position_loss = row.position - prior.position
            click_loss_ratio = (
                (prior.clicks - row.clicks) / prior.clicks if prior.clicks >= 3 else 0.0
            )
            if row.impressions >= MIN_ACTION_IMPRESSIONS and (
                position_loss >= 2 or click_loss_ratio >= 0.30
            ):
                opportunities.append(
                    Opportunity(
                        kind="DECAY",
                        issue_id=next_id("DECAY"),
                        score=max(position_loss * 2, 0) + max(prior.clicks - row.clicks, 0),
                        query=row.query,
                        page=row.page,
                        evidence=(
                            f"Position changed from {prior.position:.1f} to {row.position:.1f}; "
                            f"clicks changed from {int(prior.clicks)} to {int(row.clicks)}."
                        ),
                        action=(
                            "Inspect whether the search intent or competing results changed, verify that the page is still "
                            "indexed and internally linked, then refresh only the section that no longer answers the query."
                        ),
                    )
                )

    by_query: defaultdict[str, list[Metric]] = defaultdict(list)
    for row in current:
        if row.page and row.impressions >= MIN_CANNIBAL_IMPRESSIONS:
            by_query[row.query.casefold()].append(row)
    for rows in by_query.values():
        unique_pages = {row.page for row in rows}
        if len(unique_pages) < 2:
            continue
        ranked = sorted(rows, key=lambda item: (-item.clicks, -item.impressions, item.position or 999))
        winner = ranked[0]
        others = ", ".join(row.page for row in ranked[1:])
        opportunities.append(
            Opportunity(
                kind="CANNIBAL",
                issue_id=next_id("CANNIBAL"),
                score=sum(row.impressions for row in rows),
                query=winner.query,
                page=winner.page,
                evidence=f"The query appears for {len(unique_pages)} pages: {winner.page}, {others}.",
                action=(
                    f"Treat {winner.page} as the primary page. Point relevant internal anchors from the competing pages "
                    "to it; consolidate only if the pages genuinely serve the same buyer intent."
                ),
            )
        )

    return sorted(opportunities, key=lambda item: (-item.score, item.kind, item.query.casefold()))


def movement_status(current: Metric | None, previous: Metric | None) -> tuple[str, float | None]:
    if current and not previous:
        return "new", None
    if previous and not current:
        return "dropped", None
    if not current or not previous or current.position is None or previous.position is None:
        return "flat", None
    delta = previous.position - current.position
    if delta >= 0.5:
        return "gained", delta
    if delta <= -0.5:
        return "lost", delta
    return "flat", delta


def build_snapshot(current: list[Metric], previous: list[Metric]) -> list[dict[str, Any]]:
    current_by_key = {row.key: row for row in current}
    previous_by_key = {row.key: row for row in previous}
    all_keys = set(current_by_key) | set(previous_by_key)
    result: list[dict[str, Any]] = []

    for key in all_keys:
        now = current_by_key.get(key)
        before = previous_by_key.get(key)
        status, position_delta = movement_status(now, before)
        row = now or before
        assert row is not None
        result.append(
            {
                "keyword": row.query,
                "ranking_url": row.page,
                "clicks": round(now.clicks, 2) if now else 0,
                "previous_clicks": round(before.clicks, 2) if before else "",
                "clicks_delta": round(now.clicks - before.clicks, 2) if now and before else "",
                "impressions": round(now.impressions, 2) if now else 0,
                "previous_impressions": round(before.impressions, 2) if before else "",
                "ctr": round(now.ctr, 6) if now else 0,
                "previous_ctr": round(before.ctr, 6) if before else "",
                "average_position": round(now.position, 2) if now and now.position is not None else "",
                "previous_position": (
                    round(before.position, 2) if before and before.position is not None else ""
                ),
                "position_delta": round(position_delta, 2) if position_delta is not None else "",
                "status": status,
            }
        )

    present_queries = {str(row["keyword"]).casefold() for row in result}
    for keyword in tracked_keywords():
        if keyword.casefold() not in present_queries:
            result.append(
                {
                    "keyword": keyword,
                    "ranking_url": "",
                    "clicks": 0,
                    "previous_clicks": "",
                    "clicks_delta": "",
                    "impressions": 0,
                    "previous_impressions": "",
                    "ctr": 0,
                    "previous_ctr": "",
                    "average_position": "",
                    "previous_position": "",
                    "position_delta": "",
                    "status": "not_visible",
                }
            )
    return sorted(result, key=lambda item: (-float(item["impressions"]), str(item["keyword"]).casefold()))


def run_audit() -> tuple[bool, str]:
    process = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "seo_audit.py")],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return process.returncode == 0, process.stdout.strip()


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._"
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(value.replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def write_report(
    output_dir: Path,
    report_date: dt.date,
    source: str,
    current_period: tuple[dt.date, dt.date],
    previous_period: tuple[dt.date, dt.date],
    current: list[Metric],
    previous: list[Metric],
    markets: list[dict[str, Any]],
    snapshot: list[dict[str, Any]],
    opportunities: list[Opportunity],
    audit_ok: bool,
    audit_output: str,
    blocker: str = "",
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "rankings.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REPORT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(snapshot)
    with (output_dir / "markets.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=MARKET_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(markets)

    status_counts: defaultdict[str, int] = defaultdict(int)
    for row in snapshot:
        status_counts[str(row["status"])] += 1

    top_actions = opportunities[:5]
    if top_actions:
        summary_action = top_actions[0].action
    elif blocker:
        summary_action = "Resolve the ranking-data blocker before changing content."
    elif not current:
        summary_action = (
            "Search Console access is working; wait for Google to record impressions before changing content."
        )
    else:
        summary_action = "Keep collecting data; no opportunity met the minimum evidence thresholds this week."

    movement_rows: list[list[str]] = []
    for row in snapshot:
        if row["status"] not in {"gained", "lost", "new", "dropped"}:
            continue
        movement_rows.append(
            [
                str(row["keyword"]),
                str(row["status"]),
                str(row["average_position"] or "—"),
                str(row["previous_position"] or "—"),
                str(row["position_delta"] or "—"),
                str(row["ranking_url"] or "—"),
            ]
        )
        if len(movement_rows) == 12:
            break

    action_sections: list[str] = []
    for opportunity in top_actions:
        action_sections.append(
            f"### {opportunity.issue_id}: {opportunity.kind.title()} — {opportunity.query}\n\n"
            f"- Target: `{opportunity.page}`\n"
            f"- Evidence: {opportunity.evidence}\n"
            f"- Exact next action: {opportunity.action}\n"
            "- Publishing rule: make only this scoped change, run `python3 scripts/seo_audit.py`, "
            "then wait for the next comparable period before judging it."
        )

    market_rows = [
        [
            str(row["country"]).upper(),
            str(row["device"]),
            str(row["impressions"]),
            str(row["previous_impressions"] or "—"),
            str(row["impressions_delta"] or "—"),
            str(row["clicks"]),
            str(row["average_position"] or "—"),
        ]
        for row in markets[:20]
    ]

    content = f"""# UrbanFresh Export weekly SEO report — {report_date.isoformat()}

## Executive summary

- Data source: {source}
- Current period: {current_period[0].isoformat()} to {current_period[1].isoformat()}
- Comparison period: {previous_period[0].isoformat()} to {previous_period[1].isoformat()}
- Search rows measured: {len(current)} current, {len(previous)} previous
- Movement: {status_counts['gained']} gained, {status_counts['lost']} lost, {status_counts['new']} new, {status_counts['dropped']} dropped
- Technical audit: {'PASS' if audit_ok else 'FAIL'}
- Single most important action: {summary_action}

## Movement since the previous period

{markdown_table(['Query', 'Status', 'Position', 'Previous', 'Delta', 'Page'], movement_rows)}

## Country and device visibility

{markdown_table(['Country', 'Device', 'Impressions', 'Previous', 'Delta', 'Clicks', 'Position'], market_rows)}

## This week's evidence-backed opportunities

{chr(10).join(action_sections) if action_sections else '_No opportunity met the minimum thresholds. Do not make an SEO change only to create activity._'}

## Tracked keywords not yet visible

{', '.join(f'`{row["keyword"]}`' for row in snapshot if row['status'] == 'not_visible') or '_None._'}

## Technical audit

```text
{audit_output}
```

## Blockers and caveats

{blocker or '- Search Console reports average position, not a fixed rank. Results vary by country, device and user.\n- This free implementation intentionally does not scrape Google or use paid competitor APIs.\n- Quote leads remain the business outcome; update `seo/monthly-log.csv` during the monthly review.'}
"""
    (output_dir / "report.md").write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    load_dotenv(ROOT / ".env.local")

    final_end = args.report_date - dt.timedelta(days=3)
    current_start = final_end - dt.timedelta(days=27)
    previous_end = current_start - dt.timedelta(days=1)
    previous_start = previous_end - dt.timedelta(days=27)
    current_period = (current_start, final_end)
    previous_period = (previous_start, previous_end)

    source = "No ranking source available"
    blocker = ""
    current_rows: list[Metric] = []
    previous_rows: list[Metric] = []

    try:
        if args.current_csv:
            source = "Google Search Console CSV exports (free, local)"
            current_rows = load_search_console_csv(args.current_csv)
            previous_rows = load_search_console_csv(args.previous_csv) if args.previous_csv else []
        else:
            credentials_json = os.environ.get("GSC_CREDENTIALS_JSON", "").strip()
            if not credentials_json:
                blocker = (
                    "- `GSC_CREDENTIALS_JSON` is not configured and no `--current-csv` was supplied. "
                    "The technical baseline ran, but ranking analysis is waiting for Search Console data."
                )
                if args.verify_only:
                    print(blocker, file=sys.stderr)
                    return 2
            else:
                source = "Google Search Console API (free, read-only)"
                token = service_account_token(credentials_json)
                verify_property(token, args.site_property)
                print(f"Verified read-only Search Console access to {args.site_property}")
                if args.verify_only:
                    return 0
                current_rows = query_gsc_period(token, args.site_property, *current_period)
                previous_rows = query_gsc_period(token, args.site_property, *previous_period)
    except RuntimeError as exc:
        blocker = f"- Ranking data unavailable: {exc}"
        print(blocker, file=sys.stderr)
        if args.verify_only:
            return 2

    current = aggregate_metrics(current_rows)
    previous = aggregate_metrics(previous_rows)
    markets = build_market_snapshot(
        aggregate_market_metrics(current_rows),
        aggregate_market_metrics(previous_rows),
    )
    snapshot = build_snapshot(current, previous)
    opportunities = detect_opportunities(current, previous, args.domain)
    audit_ok, audit_output = (True, "Skipped by command option") if args.skip_audit else run_audit()
    output_dir = args.output_root / args.report_date.isoformat()
    write_report(
        output_dir,
        args.report_date,
        source,
        current_period,
        previous_period,
        current,
        previous,
        markets,
        snapshot,
        opportunities,
        audit_ok,
        audit_output,
        blocker,
    )
    print(f"Wrote {output_dir / 'rankings.csv'}")
    print(f"Wrote {output_dir / 'markets.csv'}")
    print(f"Wrote {output_dir / 'report.md'}")
    return 0 if audit_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
