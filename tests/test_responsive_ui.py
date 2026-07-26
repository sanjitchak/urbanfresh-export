from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


CSS = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")


class ResponsiveUiTests(unittest.TestCase):
    def test_fonts_and_primary_hero_images_are_discovered_from_the_head(self) -> None:
        self.assertNotIn("@import", CSS)
        for page in build_site.PAGES:
            rendered = build_site.render(page)
            hero_image = build_site.primary_image_url(page)

            self.assertIn(
                '<link rel="preconnect" href="https://fonts.googleapis.com">',
                rendered,
            )
            self.assertIn(
                '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
                rendered,
            )
            self.assertIn("fonts.googleapis.com/css2?family=Bitter", rendered)
            self.assertEqual(rendered.count('rel="preload" as="image"'), 1)
            self.assertIn(
                f'<link rel="preload" as="image" href="{hero_image}" '
                'type="image/webp" fetchpriority="high">',
                rendered,
            )

    def test_desktop_whatsapp_float_is_accessible_and_mobile_safe(self) -> None:
        generator = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
        self.assertIn('class="whatsapp-float"', generator)
        self.assertIn('aria-label="Chat with the UrbanFresh international buyer desk on WhatsApp"', generator)
        self.assertIn('<svg viewBox="0 0 24 24"', generator)
        self.assertIn("@media (min-width: 721px)", CSS)
        self.assertIn(".whatsapp-float { display: inline-flex; }", CSS)

    def test_mobile_navigation_is_anchored_to_the_sticky_header(self) -> None:
        self.assertIn("top: 100%;", CSS)
        self.assertNotIn("inset-top:", CSS)
        self.assertIn(".main-nav a { width: 100%; min-height: 48px; }", CSS)

    def test_mobile_specification_tables_stack_without_horizontal_scroll(self) -> None:
        self.assertIn(".spec-table tbody,", CSS)
        self.assertIn(".spec-table td {", CSS)
        self.assertIn("display: block;", CSS)
        self.assertIn(".content-layout > *", CSS)
        self.assertIn("min-width: 0;", CSS)

    def test_touch_and_keyboard_controls_have_durable_states(self) -> None:
        self.assertIn("flex: 0 0 44px;", CSS)
        self.assertIn(":focus-visible", CSS)
        self.assertIn("@media (prefers-reduced-motion: reduce)", CSS)
        self.assertIn("line-height: 1.1;", CSS)
        self.assertIn(".card a:not(.button)", CSS)

    def test_thank_you_page_uses_responsive_completion_components(self) -> None:
        page = (ROOT / "thank-you.html").read_text(encoding="utf-8")
        self.assertIn('class="page-thank-you"', page)
        self.assertIn('class="card completion-card"', page)
        self.assertNotIn("max-width:720px;margin:auto", page)


if __name__ == "__main__":
    unittest.main()
