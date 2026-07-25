# UrbanFresh RFQ mailer

This PHP endpoint sends two authenticated messages for every valid international
RFQ:

1. A complete lead notification to the UrbanFresh buyer desk.
2. A confirmation containing the submitted brief to the buyer.

The public website continues writing the lead to Google Sheets after the SMTP
endpoint confirms that both messages were sent.

## Hostinger layout

Deploy this directory to:

```text
/home/USER/domains/email.urbanfreshrice.com/
├── composer.json
├── config.php              # private, never committed
├── var/                    # private rate-limit counters
├── vendor/                 # installed by Composer
└── public_html/
    ├── .htaccess
    ├── index.php
    └── submit.php
```

Create `config.php` from `config.example.php`, add the mailbox password, set
permissions to `0600`, and run:

```bash
composer2 install --no-dev --optimize-autoloader
```

The production endpoint is:

```text
https://email.urbanfreshrice.com/submit.php
```

Only `https://urbanfreshrice.com` and `https://www.urbanfreshrice.com` may call
it from a browser. The endpoint validates required fields and the buyer email,
uses a honeypot, rate-limits by IP, escapes buyer content in both messages, and
does not expose SMTP errors in its response.
