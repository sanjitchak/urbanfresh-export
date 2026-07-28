# UrbanFresh shared RFQ mailer

This PHP endpoint sends two authenticated messages for every valid domestic or
international RFQ:

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

Only the HTTPS production origins for `urbanfresh.in` and
`urbanfreshrice.com`, including their redirecting `www` hosts, may call it from
a browser. This fixed allowlist lives in `public_html/submit.php`, so the
private SMTP configuration does not need to be touched when deploying the
shared endpoint. The endpoint chooses domestic or international wording from
that validated origin. It validates required fields and the buyer email, uses a
honeypot, rate-limits by IP, escapes buyer content in both messages, and does
not expose SMTP errors in its response.
