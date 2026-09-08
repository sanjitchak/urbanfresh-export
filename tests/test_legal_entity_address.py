from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


LEGAL_ENTITY = "Rajesh Industries"
ADDRESS_PARTS = (
    "119/6, Mile Stone, GT Road",
    "Opp to Neelkanth Dhaba",
    "Daha Madanpur Village, Near Namastey Chowk",
    "Karnal, Haryana - 132001, India",
)
STREET_ADDRESS = ", ".join(ADDRESS_PARTS[:3])


class LegalEntityAddressTests(unittest.TestCase):
    def test_legal_entity_and_address_are_visible_on_every_page(self) -> None:
        for page in build_site.PAGES:
            source = build_site.render(page)
            self.assertIn(LEGAL_ENTITY, source, page["slug"] or "homepage")
            for part in ADDRESS_PARTS:
                self.assertIn(part, source, page["slug"] or "homepage")

    def test_organization_schema_uses_legal_name_and_exact_address(self) -> None:
        for page in build_site.PAGES:
            source = build_site.render(page)
            scripts = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                source,
                flags=re.DOTALL,
            )
            organizations = []
            for script in scripts:
                data = json.loads(script)
                nodes = data.get("@graph", [data])
                organizations.extend(
                    node for node in nodes if node.get("@type") == "Organization"
                )
            self.assertTrue(organizations, page["slug"] or "homepage")
            organization = organizations[0]
            self.assertEqual(organization["legalName"], LEGAL_ENTITY)
            self.assertEqual(
                organization["address"]["streetAddress"], STREET_ADDRESS
            )


if __name__ == "__main__":
    unittest.main()
