import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEDULES = ROOT / "ops" / "schedules"
WORKFLOW = ROOT / ".github" / "workflows" / "weekly-seo-report.yml"


class ScheduleBackupTests(unittest.TestCase):
    def test_manifest_covers_all_recoverable_schedules(self) -> None:
        manifest = json.loads((SCHEDULES / "manifest.json").read_text(encoding="utf-8"))
        ids = {item["id"] for item in manifest["schedules"]}
        self.assertEqual(manifest["timezone"], "Asia/Kolkata")
        self.assertTrue(
            {
                "domestic-github-quality",
                "export-github-quality",
                "domestic-github-gsc-report",
                "export-github-gsc-report",
                "com.urbanfresh.seo-improver",
                "urbanfresh-weekly-seo-monitor",
                "urbanfresh-monthly-seo-loop",
            }.issubset(ids)
        )

    def test_codex_specs_are_portable_and_contain_no_local_absolute_path(self) -> None:
        for name in ("codex-weekly-monitor.md", "codex-monthly-optimizer.md"):
            text = (SCHEDULES / name).read_text(encoding="utf-8")
            self.assertIn("${RICE_BUSINESS_ROOT}", text)
            self.assertNotIn("/Users/Administrator/", text)
            self.assertNotIn("private_key", text)

    def test_cloud_report_is_scheduled_and_retained(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('cron: "0 4 * * 1"', text)
        self.assertIn("GSC_CREDENTIALS_JSON", text)
        self.assertIn("actions/upload-artifact@v4", text)
        self.assertIn("retention-days: 90", text)
        self.assertIn("workflow_dispatch:", text)


if __name__ == "__main__":
    unittest.main()
