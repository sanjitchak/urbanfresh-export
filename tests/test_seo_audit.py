from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import seo_audit  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
