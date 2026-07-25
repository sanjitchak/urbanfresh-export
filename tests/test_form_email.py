from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JS = (ROOT / "assets/js/site.js").read_text(encoding="utf-8")
GENERATOR = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
ENDPOINT = (ROOT / "server/public_html/submit.php").read_text(encoding="utf-8")
CONFIG = (ROOT / "server/config.example.php").read_text(encoding="utf-8")


class FormEmailTests(unittest.TestCase):
    def test_form_requires_buyer_email_and_includes_honeypot(self) -> None:
        self.assertIn("const requiredNames = ['name', 'phone', 'email', 'location', 'quantity'];", JS)
        self.assertIn('Business email *', GENERATOR)
        self.assertIn('name="website"', GENERATOR)

    def test_frontend_uses_private_email_endpoint_before_sheet_backup(self) -> None:
        endpoint_call = JS.index("await fetch(EMAIL_ENDPOINT")
        sheet_call = JS.index("await fetch(GOOGLE_SHEETS_ENDPOINT")
        self.assertLess(endpoint_call, sheet_call)
        self.assertIn("https://email.urbanfreshrice.com/submit.php", JS)

    def test_endpoint_restricts_origins_and_keeps_smtp_secret_external(self) -> None:
        self.assertIn("'HTTP_ORIGIN'", ENDPOINT)
        self.assertIn("'Origin is not allowed.'", ENDPOINT)
        self.assertIn("require $configFile", ENDPOINT)
        self.assertNotIn("REPLACE_WITH_HOSTINGER_MAILBOX_PASSWORD", ENDPOINT)
        self.assertIn("REPLACE_WITH_HOSTINGER_MAILBOX_PASSWORD", CONFIG)

    def test_endpoint_sends_owner_and_buyer_messages(self) -> None:
        self.assertIn("sendOwnerNotification($config, $fields, $safeLeadId);", ENDPOINT)
        self.assertIn("sendBuyerConfirmation($config, $fields, $safeLeadId);", ENDPOINT)
        self.assertIn("addReplyTo($fields['email'], $fields['name'])", ENDPOINT)
        self.assertIn("We received your rice RFQ", ENDPOINT)
        self.assertIn("'notification_email' => 'sanjit@growonlinetoday.com'", CONFIG)


if __name__ == "__main__":
    unittest.main()
