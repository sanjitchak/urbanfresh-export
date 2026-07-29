#!/usr/bin/env python3
"""Local, zero-cost technical SEO checks for the UrbanFresh Export static site."""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "urbanfreshrice.com"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_h1 = False
        self.in_jsonld = False
        self.title_parts: list[str] = []
        self.h1_parts: list[str] = []
        self.h1_count = 0
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.links: list[str] = []
        self.hreflangs: dict[str, str] = {}
        self.images_missing_alt: list[str] = []
        self.jsonld_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
            self.h1_count += 1
        elif tag == "meta" and values.get("name", "").lower() == "description":
            self.description = values.get("content", "") or ""
        elif tag == "meta" and values.get("name", "").lower() == "robots":
            self.robots = values.get("content", "") or ""
        elif tag == "link" and "canonical" in (values.get("rel", "") or "").lower():
            self.canonical = values.get("href", "") or ""
        elif tag == "link" and "alternate" in (values.get("rel", "") or "").lower() and values.get("hreflang"):
            self.hreflangs[values["hreflang"] or ""] = values.get("href", "") or ""
        elif tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        elif tag == "img" and "alt" not in values:
            self.images_missing_alt.append(values.get("src", "unknown image") or "unknown image")
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self.in_jsonld = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False
        elif tag == "script" and self.in_jsonld:
            self.in_jsonld = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_h1:
            self.h1_parts.append(data)
        if self.in_jsonld:
            self.jsonld_parts.append(data)


def clean(parts: list[str]) -> str:
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def internal_target(source: Path, href: str) -> Path | None:
    if not href or href.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if not path:
        return None
    target = (source.parent / path).resolve()
    if target.is_dir():
        target /= "index.html"
    return target


def json_objects(value: object):
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from json_objects(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from json_objects(nested)


def unsupported_product_snippets(data: object) -> list[str]:
    unsupported: list[str] = []
    for node in json_objects(data):
        node_type = node.get("@type")
        types = node_type if isinstance(node_type, list) else [node_type]
        if "Product" not in types:
            continue
        if any(node.get(required) for required in ("offers", "review", "aggregateRating")):
            continue
        unsupported.append(str(node.get("name", "unnamed Product")))
    return unsupported


def datasets_missing_license(data: object) -> list[str]:
    missing: list[str] = []
    for node in json_objects(data):
        node_type = node.get("@type")
        types = node_type if isinstance(node_type, list) else [node_type]
        if "Dataset" not in types:
            continue
        if node.get("license"):
            continue
        missing.append(str(node.get("name", "unnamed Dataset")))
    return missing


def audit() -> int:
    pages = sorted(ROOT.glob("*.html"))
    errors: list[str] = []
    warnings: list[str] = []
    canonicals: dict[str, str] = {}
    page_hreflangs: dict[str, dict[str, str]] = {}

    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        title = clean(parser.title_parts)
        h1 = clean(parser.h1_parts)
        label = page.name

        if not title:
            errors.append(f"{label}: missing title")
        elif not 30 <= len(title) <= 65:
            warnings.append(f"{label}: title length {len(title)} (aim 30-65)")
        if not parser.description:
            errors.append(f"{label}: missing meta description")
        elif not 110 <= len(parser.description) <= 170:
            warnings.append(f"{label}: description length {len(parser.description)} (aim 110-170)")
        if parser.h1_count != 1:
            errors.append(f"{label}: expected one H1, found {parser.h1_count}")
        if not h1:
            errors.append(f"{label}: H1 is empty")
        if not parser.canonical:
            errors.append(f"{label}: missing canonical")
        elif urlsplit(parser.canonical).netloc != DOMAIN:
            errors.append(f"{label}: canonical must use {DOMAIN}")
        elif parser.canonical in canonicals:
            errors.append(f"{label}: duplicate canonical also used by {canonicals[parser.canonical]}")
        else:
            canonicals[parser.canonical] = label
            page_hreflangs[parser.canonical] = parser.hreflangs
        if parser.images_missing_alt:
            errors.append(f"{label}: image(s) missing alt: {', '.join(parser.images_missing_alt)}")
        if not clean(parser.jsonld_parts):
            warnings.append(f"{label}: no JSON-LD structured data")
        else:
            try:
                structured_data = json.loads(clean(parser.jsonld_parts))
                unsupported = unsupported_product_snippets(structured_data)
                if unsupported:
                    errors.append(
                        f"{label}: Product markup lacks offers, review or aggregateRating: "
                        f"{', '.join(unsupported)}"
                    )
                unlicensed_datasets = datasets_missing_license(structured_data)
                if unlicensed_datasets:
                    errors.append(
                        f"{label}: Dataset markup lacks license: "
                        f"{', '.join(unlicensed_datasets)}"
                    )
            except json.JSONDecodeError as exc:
                errors.append(f"{label}: invalid JSON-LD ({exc.msg})")

        for href in parser.links:
            target = internal_target(page, href)
            if target and ROOT in target.parents and not target.exists():
                errors.append(f"{label}: broken internal link {href}")

    sitemap = ROOT / "sitemap.xml"
    robots = ROOT / "robots.txt"
    if not sitemap.exists():
        errors.append("site: sitemap.xml missing")
    if not robots.exists():
        errors.append("site: robots.txt missing")
    elif "Disallow: /" in robots.read_text(encoding="utf-8"):
        for page in pages:
            parser = PageParser()
            parser.feed(page.read_text(encoding="utf-8"))
            if "noindex" not in parser.robots.lower():
                errors.append(f"{page.name}: crawler-blocked site must be noindex")

    hreflang_map = ROOT / "seo" / "hreflang-map.json"
    if hreflang_map.exists():
        try:
            pairs = json.loads(hreflang_map.read_text(encoding="utf-8")).get("pairs", [])
        except (json.JSONDecodeError, AttributeError):
            errors.append("site: invalid seo/hreflang-map.json")
            pairs = []
        for pair in pairs:
            if not isinstance(pair, dict) or set(pair) != {"en-IN", "en"}:
                errors.append("site: each hreflang pair must contain en-IN and en")
                continue
            local_urls = [url for url in pair.values() if urlsplit(url).netloc == DOMAIN]
            if len(local_urls) != 1:
                errors.append(f"site: hreflang pair must contain exactly one {DOMAIN} URL")
                continue
            local_url = local_urls[0]
            actual = page_hreflangs.get(local_url)
            if actual is None:
                errors.append(f"site: hreflang local page missing from generated canonicals: {local_url}")
            elif actual != pair:
                errors.append(f"{canonicals[local_url]}: hreflang declarations do not match reciprocal map")

    print(f"UrbanFresh Export SEO audit: {len(pages)} HTML pages")
    if errors:
        print("\nERRORS")
        for item in errors:
            print(f"- {item}")
    if warnings:
        print("\nWARNINGS")
        for item in warnings:
            print(f"- {item}")
    if not errors and not warnings:
        print("PASS: all local checks passed")
    elif not errors:
        print("\nPASS with advisory warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(audit())
