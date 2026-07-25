from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402
import submit_sitemap  # noqa: E402


class LaunchBuildTests(unittest.TestCase):
    def test_site_is_launch_ready(self) -> None:
        self.assertTrue(build_site.LAUNCH_READY)

    def test_generated_launch_pages_are_indexable(self) -> None:
        for page in build_site.PAGES:
            output = build_site.render(page)
            expected = "noindex,nofollow" if page["slug"] == "thank-you.html" else "index,follow,max-image-preview:large"
            self.assertIn(f'name="robots" content="{expected}"', output)

    def test_robots_allows_crawlers(self) -> None:
        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Allow: /", robots)
        self.assertNotIn("Disallow: /", robots)

    def test_sitemap_uses_export_domain(self) -> None:
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        locations = [
            node.text or ""
            for node in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/"
                                     "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        ]
        self.assertTrue(locations)
        self.assertTrue(all(url.startswith("https://urbanfreshrice.com/") for url in locations))


class SitemapSubmissionTests(unittest.TestCase):
    def test_wait_for_live_accepts_matching_sitemap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sitemap.xml"
            path.write_bytes(b"<urlset></urlset>\n")
            with mock.patch.object(
                submit_sitemap,
                "fetch_live_sitemap",
                return_value=b"<urlset></urlset>\n",
            ):
                submit_sitemap.wait_for_live_sitemap(
                    path,
                    "https://urbanfreshrice.com/sitemap.xml",
                    timeout=0,
                )

    def test_dry_run_uses_export_property_without_credentials(self) -> None:
        with mock.patch("builtins.print") as output:
            exit_code = submit_sitemap.main(["--dry-run"])
        self.assertEqual(exit_code, 0)
        rendered = " ".join(str(call) for call in output.call_args_list)
        self.assertIn("sc-domain:urbanfreshrice.com", rendered)
        self.assertIn("https://urbanfreshrice.com/sitemap.xml", rendered)


if __name__ == "__main__":
    unittest.main()
