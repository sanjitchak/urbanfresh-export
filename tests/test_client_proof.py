from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA_IDS = ("lxjkrtdi02", "l82atxvvng", "8bg0co98z9")


class ClientProofTests(unittest.TestCase):
    def test_client_proof_page_uses_three_wistia_embeds(self) -> None:
        page = (ROOT / "client-proof.html").read_text(encoding="utf-8")
        self.assertIn("https://fast.wistia.com/player.js", page)
        for media_id in MEDIA_IDS:
            self.assertIn(f"https://fast.wistia.com/embed/{media_id}.js", page)
            self.assertIn(f'<wistia-player media-id="{media_id}"', page)
        self.assertNotIn("<video", page)
        self.assertNotIn(".mp4", page)

    def test_page_keeps_loading_claims_within_the_supplied_evidence(self) -> None:
        page = (ROOT / "client-proof.html").read_text(encoding="utf-8")
        self.assertIn("Loading 10 metric tons.", page)
        self.assertIn("Loading 125 metric tons.", page)
        self.assertIn("They do not identify the buyer", page)
        self.assertIn("whether any export movement was direct or through a merchant exporter", page)

    def test_homepage_and_footer_link_to_client_proof(self) -> None:
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(homepage.count('href="client-proof.html"'), 2)


if __name__ == "__main__":
    unittest.main()
