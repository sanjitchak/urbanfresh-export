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

    def test_sitemap_exactly_matches_indexable_pages_and_lists_real_images(self) -> None:
        sitemap_ns = build_site.SITEMAP_NS
        image_ns = build_site.IMAGE_SITEMAP_NS
        root = ET.parse(ROOT / "sitemap.xml").getroot()
        url_nodes = root.findall(f"{{{sitemap_ns}}}url")
        actual_locations = {
            node.findtext(f"{{{sitemap_ns}}}loc", default="")
            for node in url_nodes
        }
        expected_locations = {
            build_site.page_url(page)
            for page in build_site.PAGES
            if page["slug"] != "thank-you.html"
        }

        self.assertEqual(actual_locations, expected_locations)
        for node in url_nodes:
            lastmod = node.findtext(f"{{{sitemap_ns}}}lastmod", default="")
            self.assertRegex(lastmod, r"^\d{4}-\d{2}-\d{2}$")
            image_locations = [
                image.text or ""
                for image in node.findall(
                    f"{{{image_ns}}}image/{{{image_ns}}}loc"
                )
            ]
            self.assertTrue(image_locations)
            for image_url in image_locations:
                self.assertTrue(image_url.startswith(f"{build_site.DOMAIN}/assets/images/"))
                local_path = ROOT / image_url.removeprefix(f"{build_site.DOMAIN}/")
                self.assertTrue(local_path.exists(), image_url)

    def test_stable_lastmod_changes_only_when_rendered_html_changes(self) -> None:
        url = "https://urbanfreshrice.com/1121-basmati-rice.html"
        previous = {url: "2026-07-25"}

        self.assertEqual(
            build_site.stable_lastmod(url, "<html>same</html>", "<html>same</html>", previous),
            "2026-07-25",
        )
        self.assertEqual(
            build_site.stable_lastmod(url, "<html>old</html>", "<html>new</html>", previous),
            build_site.BUILD_DATE,
        )


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
