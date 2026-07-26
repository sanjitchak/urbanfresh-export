from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import submit_indexnow  # noqa: E402


class IndexNowSubmissionTests(unittest.TestCase):
    def test_repository_key_matches_the_configured_key(self) -> None:
        self.assertEqual(
            submit_indexnow.read_key(submit_indexnow.DEFAULT_KEY_FILE),
            submit_indexnow.DEFAULT_KEY,
        )

    def test_repository_sitemap_contains_only_the_configured_host(self) -> None:
        urls = submit_indexnow.sitemap_urls(
            ROOT / "sitemap.xml",
            submit_indexnow.DEFAULT_HOST,
        )
        self.assertTrue(urls)
        self.assertTrue(
            all(url.startswith("https://urbanfreshrice.com/") for url in urls)
        )

    def test_sitemap_rejects_a_foreign_host(self) -> None:
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://example.com/foreign.html</loc></url>
</urlset>
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sitemap.xml"
            path.write_text(sitemap, encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "urbanfreshrice.com"):
                submit_indexnow.sitemap_urls(path, "urbanfreshrice.com")

    def test_sitemap_ignores_nested_image_locations(self) -> None:
        sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
  <url>
    <loc>https://urbanfreshrice.com/contact.html</loc>
    <image:image><image:loc>https://urbanfreshrice.com/assets/contact.webp</image:loc></image:image>
  </url>
</urlset>
"""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sitemap.xml"
            path.write_text(sitemap, encoding="utf-8")
            urls = submit_indexnow.sitemap_urls(path, "urbanfreshrice.com")
        self.assertEqual(urls, ["https://urbanfreshrice.com/contact.html"])

    def test_wait_for_live_key_retries_until_it_matches(self) -> None:
        with mock.patch.object(
            submit_indexnow,
            "fetch_live_key",
            side_effect=["not-the-key", submit_indexnow.DEFAULT_KEY],
        ) as fetch:
            submit_indexnow.wait_for_live_key(
                submit_indexnow.DEFAULT_KEY_LOCATION,
                submit_indexnow.DEFAULT_KEY,
                timeout=1,
                poll_interval=0,
            )
        self.assertEqual(fetch.call_count, 2)

    def test_json_submission_uses_post_and_expected_payload(self) -> None:
        captured: dict[str, object] = {}

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self) -> bytes:
                return b""

        def fake_urlopen(request, timeout):
            captured["request"] = request
            captured["timeout"] = timeout
            return Response()

        urls = [
            "https://urbanfreshrice.com/",
            "https://urbanfreshrice.com/contact.html",
        ]
        with mock.patch.object(
            submit_indexnow.urllib.request,
            "urlopen",
            side_effect=fake_urlopen,
        ):
            status = submit_indexnow.submit_urls(
                submit_indexnow.DEFAULT_ENDPOINT,
                submit_indexnow.DEFAULT_HOST,
                submit_indexnow.DEFAULT_KEY,
                submit_indexnow.DEFAULT_KEY_LOCATION,
                urls,
            )

        request = captured["request"]
        self.assertEqual(status, 200)
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(json.loads(request.data.decode("utf-8"))["urlList"], urls)

    def test_dry_run_does_not_make_network_requests(self) -> None:
        with (
            mock.patch.object(submit_indexnow, "verify_live_key") as verify,
            mock.patch.object(submit_indexnow, "submit_urls") as submit,
        ):
            exit_code = submit_indexnow.main(["--dry-run"])
        self.assertEqual(exit_code, 0)
        verify.assert_not_called()
        submit.assert_not_called()


if __name__ == "__main__":
    unittest.main()
