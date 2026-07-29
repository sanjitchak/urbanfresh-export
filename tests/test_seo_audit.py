from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import seo_audit  # noqa: E402
import build_site  # noqa: E402


class ProductSnippetAuditTests(unittest.TestCase):
    def test_product_without_offer_review_or_rating_is_rejected(self) -> None:
        data = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "Product", "name": "1121 Basmati Rice"},
            ],
        }

        self.assertEqual(
            seo_audit.unsupported_product_snippets(data),
            ["1121 Basmati Rice"],
        )

    def test_product_with_truthful_offer_is_allowed(self) -> None:
        data = {
            "@type": "Product",
            "name": "Example Product",
            "offers": {
                "@type": "Offer",
                "price": 100,
                "priceCurrency": "INR",
            },
        }

        self.assertEqual(seo_audit.unsupported_product_snippets(data), [])

    def test_item_page_does_not_claim_product_rich_result(self) -> None:
        data = {
            "@type": "ItemPage",
            "name": "1121 Basmati Rice",
            "mainEntity": {"@type": "Thing", "name": "1121 Basmati Rice"},
        }

        self.assertEqual(seo_audit.unsupported_product_snippets(data), [])


class DatasetAuditTests(unittest.TestCase):
    def test_dataset_without_license_is_rejected(self) -> None:
        data = {
            "@type": "Dataset",
            "name": "Example export dataset",
            "description": "An example dataset without stated use terms.",
        }

        self.assertEqual(
            seo_audit.datasets_missing_license(data),
            ["Example export dataset"],
        )

    def test_every_generated_page_has_no_unlicensed_dataset(self) -> None:
        for page in build_site.PAGES:
            self.assertEqual(
                seo_audit.datasets_missing_license(build_site.page_schema(page)),
                [],
                page["slug"] or "index.html",
            )


class GeneratedSchemaTests(unittest.TestCase):
    def test_page_graph_uses_stable_entity_ids_and_truthful_breadcrumbs(self) -> None:
        page = next(
            item for item in build_site.PAGES
            if item["slug"] == "1121-basmati-rice.html"
        )
        data = build_site.page_schema(page)
        graph = data["@graph"]
        by_id = {
            node["@id"]: node
            for node in graph
            if isinstance(node, dict) and node.get("@id")
        }
        page_url = build_site.page_url(page)

        self.assertIn(f"{build_site.DOMAIN}/#organization", by_id)
        self.assertIn(f"{build_site.DOMAIN}/#website", by_id)
        self.assertIn(f"{page_url}#webpage", by_id)
        self.assertIn(f"{page_url}#primaryimage", by_id)
        self.assertIn(f"{page_url}#breadcrumb", by_id)

        webpage = by_id[f"{page_url}#webpage"]
        self.assertEqual(webpage["isPartOf"], {"@id": f"{build_site.DOMAIN}/#website"})
        self.assertEqual(webpage["about"], {"@id": f"{build_site.DOMAIN}/#organization"})
        self.assertEqual(webpage["breadcrumb"], {"@id": f"{page_url}#breadcrumb"})
        self.assertEqual(webpage["inLanguage"], "en")

        breadcrumb = by_id[f"{page_url}#breadcrumb"]
        items = breadcrumb["itemListElement"]
        self.assertEqual(
            [(item["position"], item["name"], item["item"]) for item in items],
            [
                (1, "Home", f"{build_site.DOMAIN}/"),
                (2, "Rice", page_url),
            ],
        )

    def test_homepage_graph_defines_site_name_without_fake_breadcrumb(self) -> None:
        homepage = next(item for item in build_site.PAGES if not item["slug"])
        data = build_site.page_schema(homepage)
        graph = data["@graph"]
        website = next(node for node in graph if node.get("@type") == "WebSite")

        self.assertEqual(website["@id"], f"{build_site.DOMAIN}/#website")
        self.assertEqual(website["name"], "UrbanFresh International")
        self.assertFalse(any(node.get("@type") == "BreadcrumbList" for node in graph))


if __name__ == "__main__":
    unittest.main()
