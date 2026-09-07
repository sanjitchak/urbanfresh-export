from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEDIA_ID = "lxjkrtdi02"


class HeroVideoTests(unittest.TestCase):
    def test_homepage_has_background_video_and_image_fallback(self) -> None:
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(f"https://fast.wistia.com/embed/{MEDIA_ID}.js", homepage)
        self.assertIn(f'<wistia-player media-id="{MEDIA_ID}"', homepage)
        self.assertIn('fit-strategy="cover"', homepage)
        self.assertIn("--hero-image:url('/assets/images/ricefarm/mill-processing-plant.webp')", homepage)

    def test_video_is_home_only_and_text_stays_above_overlay(self) -> None:
        css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
        self.assertIn(".hero-video wistia-player:defined { opacity: 1; }", css)
        self.assertIn(".hero-inner { position: relative; z-index: 2;", css)
        self.assertIn(".hero-video { display: none; }", css)
        for page in ROOT.glob("*.html"):
            if page.name != "index.html":
                self.assertNotIn("fast.wistia.com/player.js", page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
