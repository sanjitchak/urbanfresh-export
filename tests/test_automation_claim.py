from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


CLAIM = "Our production facility is fully automated."


class AutomationClaimTests(unittest.TestCase):
    def test_claim_is_visible_on_every_generated_page(self) -> None:
        for page in build_site.PAGES:
            self.assertIn(CLAIM, build_site.render(page), page["slug"] or "homepage")

    def test_generator_owns_the_sitewide_claim(self) -> None:
        generator = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
        self.assertIn(f'AUTOMATION_CLAIM = "{CLAIM}"', generator)
        self.assertIn("Fully automated production facility", generator)


if __name__ == "__main__":
    unittest.main()
