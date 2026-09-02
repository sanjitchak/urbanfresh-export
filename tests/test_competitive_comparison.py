from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class CompetitiveComparisonTests(unittest.TestCase):
    def test_homepage_contains_aggressive_factual_comparison(self) -> None:
        homepage = build_site.render(build_site.PAGES[0])
        self.assertIn("UrbanFresh versus weak offers", homepage)
        self.assertIn("Stop buying rice on promises. Buy against proof.", homepage)
        self.assertIn("The UrbanFresh advantage", homepage)
        self.assertIn("What a weak offer looks like", homepage)
        self.assertEqual(homepage.count('class="advantage-row"'), 5)

    def test_comparison_is_responsive_and_source_owned(self) -> None:
        source = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        self.assertIn("Lot-specific evidence reviewed against the destination brief.", source)
        self.assertIn(".advantage-row", css)
        self.assertIn(".advantage-head { display: none; }", css)


if __name__ == "__main__":
    unittest.main()
