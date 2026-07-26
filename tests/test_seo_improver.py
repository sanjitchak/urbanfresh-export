from __future__ import annotations

import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import seo_improver  # noqa: E402


class SeoImproverTests(unittest.TestCase):
    def test_http_date_epoch_uses_utc_server_time(self) -> None:
        epoch = seo_improver.http_date_epoch("Wed, 15 Jul 2026 02:15:02 GMT")

        self.assertEqual(epoch, 1784081702)

    def test_load_dotenv_accepts_raw_service_account_json(self) -> None:
        original = os.environ.pop("GSC_CREDENTIALS_JSON", None)
        try:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / ".env.local"
                path.write_text(
                    json.dumps(
                        {
                            "type": "service_account",
                            "client_email": "seo@example.iam.gserviceaccount.com",
                            "private_key": "private-key-placeholder",
                        }
                    ),
                    encoding="utf-8",
                )

                seo_improver.load_dotenv(path)

            loaded = json.loads(os.environ["GSC_CREDENTIALS_JSON"])
            self.assertEqual(loaded["type"], "service_account")
            self.assertEqual(loaded["client_email"], "seo@example.iam.gserviceaccount.com")
        finally:
            os.environ.pop("GSC_CREDENTIALS_JSON", None)
            if original is not None:
                os.environ["GSC_CREDENTIALS_JSON"] = original

    def test_csv_loader_accepts_search_console_headers_and_percent_ctr(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gsc.csv"
            with path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Top queries", "Clicks", "Impressions", "CTR", "Position"])
                writer.writerow(["1121 basmati rice supplier", "4", "120", "3.33%", "9.4"])

            rows = seo_improver.load_search_console_csv(path)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].query, "1121 basmati rice supplier")
        self.assertEqual(rows[0].clicks, 4)
        self.assertAlmostEqual(rows[0].ctr, 0.0333)
        self.assertEqual(rows[0].position, 9.4)

    def test_aggregate_metrics_weights_position_by_impressions(self) -> None:
        rows = [
            seo_improver.Metric("rice mill", "https://urbanfreshrice.com/", 1, 10, 0.1, 5),
            seo_improver.Metric("rice mill", "https://urbanfreshrice.com/", 3, 30, 0.1, 9),
        ]

        result = seo_improver.aggregate_metrics(rows)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].clicks, 4)
        self.assertEqual(result[0].impressions, 40)
        self.assertEqual(result[0].position, 8)

    def test_country_and_device_dimensions_are_preserved_and_aggregated(self) -> None:
        rows = [
            seo_improver.Metric(
                "1121 basmati rice supplier",
                "https://urbanfreshrice.com/1121-basmati-rice.html",
                1,
                10,
                0.1,
                5,
                "MOBILE",
                "usa",
            ),
            seo_improver.Metric(
                "basmati rice supplier",
                "https://urbanfreshrice.com/",
                3,
                30,
                0.1,
                9,
                "MOBILE",
                "usa",
            ),
            seo_improver.Metric(
                "basmati rice supplier",
                "https://urbanfreshrice.com/",
                2,
                20,
                0.1,
                7,
                "DESKTOP",
                "gbr",
            ),
        ]

        markets = seo_improver.aggregate_market_metrics(rows)
        usa_mobile = next(
            row for row in markets if row.country == "usa" and row.device == "MOBILE"
        )

        self.assertEqual(usa_mobile.clicks, 4)
        self.assertEqual(usa_mobile.impressions, 40)
        self.assertEqual(usa_mobile.position, 8)
        self.assertEqual(
            {(row.country, row.device) for row in markets},
            {("usa", "MOBILE"), ("gbr", "DESKTOP")},
        )

    def test_market_snapshot_keeps_country_device_comparisons_separate(self) -> None:
        current = [
            seo_improver.MarketMetric("usa", "MOBILE", 3, 30, 0.1, 8),
            seo_improver.MarketMetric("are", "DESKTOP", 1, 10, 0.1, 12),
        ]
        previous = [
            seo_improver.MarketMetric("usa", "MOBILE", 1, 20, 0.05, 10),
        ]

        snapshot = seo_improver.build_market_snapshot(current, previous)
        usa = next(row for row in snapshot if row["country"] == "usa")

        self.assertEqual(usa["impressions_delta"], 10)
        self.assertEqual(usa["position_delta"], 2)
        self.assertEqual(len(snapshot), 2)

    def test_detects_striking_distance_low_ctr_and_decay(self) -> None:
        current = [
            seo_improver.Metric(
                "1121 basmati rice supplier",
                "https://urbanfreshrice.com/1121-basmati-rice.html",
                1,
                100,
                0.01,
                10,
            )
        ]
        previous = [
            seo_improver.Metric(
                "1121 basmati rice supplier",
                "https://urbanfreshrice.com/1121-basmati-rice.html",
                5,
                100,
                0.05,
                7,
            )
        ]

        opportunities = seo_improver.detect_opportunities(current, previous, "urbanfreshrice.com")
        kinds = {item.kind for item in opportunities}

        self.assertIn("STRIKE", kinds)
        self.assertIn("CTR", kinds)
        self.assertIn("DECAY", kinds)

    def test_weak_samples_do_not_trigger_content_changes(self) -> None:
        current = [
            seo_improver.Metric(
                "basmati rice supplier",
                "https://urbanfreshrice.com/",
                0,
                10,
                0,
                9,
            )
        ]
        previous = [
            seo_improver.Metric(
                "basmati rice supplier",
                "https://urbanfreshrice.com/",
                1,
                10,
                0.1,
                5,
            )
        ]

        opportunities = seo_improver.detect_opportunities(
            current,
            previous,
            "urbanfreshrice.com",
        )

        self.assertEqual(opportunities, [])

    def test_snapshot_keeps_missing_seed_keywords_visible(self) -> None:
        snapshot = seo_improver.build_snapshot([], [])

        self.assertTrue(snapshot)
        self.assertTrue(all(row["status"] == "not_visible" for row in snapshot))


if __name__ == "__main__":
    unittest.main()
