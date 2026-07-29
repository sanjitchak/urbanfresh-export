# UrbanFresh Export project handoff

## Current state

- Repository: `sanjitchak/urbanfresh-export`, default branch `main`
- Intended production domain: `https://urbanfreshrice.com/`
- Production site: `https://urbanfreshrice.com/`
- Deployment: GitHub Pages from `main`; HTTPS enforced
- Domestic website: `https://urbanfresh.in/`
- Search Console property: `sc-domain:urbanfreshrice.com`, verified
- Discovery automation: SEO-relevant pushes wait for the live sitemap and
  IndexNow key, submit and verify the sitemap in Search Console, then notify
  IndexNow
- Monitoring: weekly GitHub quality checks and a Monday 09:30 AM IST read-only
  dual-domain monitor; the evidence-gated monthly optimizer remains active on
  the first Monday at 10:00 AM IST

## Open items

- Search Console is processing the newly verified property. Monitor its first
  indexing and performance data together with the next Ubersuggest rank refresh
  on 2026-08-01.

## Change history

### 2026-07-29 — Dataset license guard mirrored from the domestic site

- Confirmed the international generator does not currently publish any
  `Dataset` entity, so no unsupported dataset or license claim was added.
- Extended the export SEO audit to reject any future Dataset structured data
  that omits an explicit license.
- Added regression coverage across every generated export-page graph so the
  guard remains enforced if structured data changes later.
- Rebuilt all 11 pages; the SEO audit, PHP syntax, Composer validation, all 44
  tests, dry-run sitemap and IndexNow checks, and `git diff --check` passed.
- Published commit `408898c`; Pages run `30447676986` and SEO quality run
  `30447678829` succeeded. The generated and live export pages remain free of
  Dataset claims, so no new license or commercial-use statement was published.

### 2026-07-29 — Shared SMTP mailer extended to the domestic website

- Extended the existing Hostinger PHP endpoint's fixed allowlist to accept the
  validated HTTPS origins for both `urbanfresh.in` and
  `urbanfreshrice.com`, without changing the private SMTP configuration.
- Added origin-specific domestic and international owner subjects, buyer
  wording, field labels and footer labels while preserving the same SMTP
  credential, owner recipient, buyer confirmation, validation, honeypot,
  rate-limit and escaping controls.
- Updated the public configuration template, deployment documentation and
  regression coverage. No SMTP password or private production configuration was
  added to Git.

### 2026-07-28 — SEO schedules backed up for hardware recovery

- Added a mirrored, secret-free recovery pack that inventories every domestic
  and international SEO schedule and preserves the exact Codex weekly-monitor
  and monthly-optimizer specifications with portable path placeholders.
- Documented clean-machine recovery, including the domestic repo's single
  two-domain macOS LaunchAgent, current-project Codex recreation, and the
  encrypted GitHub secret that must be restored separately after a repository
  transfer.
- Kept the existing Monday 09:00 IST technical checks cloud-hosted while
  excluding private Search Console report data and credentials from the
  repository. Added regression coverage for schedule completeness, path
  portability and credential exclusion.
- Existing active local and Codex schedules were preserved and not duplicated.
- Published the privacy-safe recovery state through commit `e9c7ece`; SEO
  quality run `30310976669` and Pages run `30310975852` succeeded. The current
  workflow list contains no cloud report uploader, and no export report run or
  artifact was created.

### 2026-07-26 — SEO generator and entity markup hardened

- Replaced rebuild-wide sitemap dates with stable per-page `lastmod` values:
  an existing date is retained when the generated HTML is unchanged and only a
  significant rendered-page change receives the current build date.
- Added image-sitemap entries for each page's primary photograph and additional
  visible content photography, while keeping the noindex thank-you page out of
  the sitemap.
- Connected Organization, WebSite, WebPage/ItemPage and primary-image entities
  with stable JSON-LD identifiers, and added BreadcrumbList data that matches
  the visible two-level breadcrumb trail.
- Removed the render-blocking Google Fonts CSS `@import` waterfall while
  retaining the same families and weights: generated pages now preconnect to
  the font origins and load the stylesheet directly from the document head.
  Each page also preloads its existing primary hero WebP so the
  CSS-background LCP candidate is discoverable before stylesheet processing.
- Added focused regression coverage for exact sitemap/indexable-page parity,
  real local image URLs, stable modification dates and the structured-data
  graph, plus font and primary-image discovery. Ignored generated SEO reports
  and the owner-supplied `Skill design/` reference folder.
- Added a public per-domain IndexNow verification key and guarded standard-
  library submitter. SEO-relevant deployments now wait for the live key, then
  notify IndexNow after the authenticated Google sitemap handoff. A separate
  weekly GitHub quality job rebuilds the site, rejects generated drift and runs
  the full audit/test suite.
- Preserved Search Console country and device dimensions in a separate
  `markets.csv` report so the United States, United Kingdom, United Arab
  Emirates, India and device results are no longer merged. Raised automatic
  content-opportunity thresholds to 100 impressions so weak samples cannot
  trigger page changes.
- Copied the already approved Search Console service-account configuration into
  the export repository's ignored `.env.local` with owner-only permissions.
  A live read-only API run verified access and correctly reported that the new
  property still has no performance rows; no credential was printed or added
  to Git.
- Rebuilt all 11 generated pages. The SEO audit, all 39 unit tests, Search
  Console and IndexNow dry-runs, rendered 390/1440 px checks, and
  `git diff --check` passed.
- Published commit `942d3ff`. GitHub Pages run `30185522913`, weekly-quality
  run `30185523405` and discovery run `30185523411` succeeded. The live sitemap
  matched the repository byte-for-byte, Search Console recorded the submission
  at `2026-07-26T03:03:15.685Z`, and IndexNow accepted all 10 canonical URLs
  with HTTP 202.

### 2026-07-26 — Desktop WhatsApp floating icon added

- Added an accessible circular WhatsApp icon to every international-site page,
  linked to the existing prefilled buyer-desk chat.
- Limited the floating control to desktop layouts so it cannot compete with the
  existing mobile bottom CTA.
- Rebuilt all 11 pages and verified the rendered 60 px control at desktop width;
  the SEO audit, all 24 unit tests and `git diff --check` passed.
- Published commit `511721e`; GitHub Pages deployment `30169553355` and Search
  Console sitemap workflow `30169553856` succeeded. Live desktop QA confirmed
  the new stylesheet, circular icon and prefilled international RFQ link.

### 2026-07-25 — RFQ owner recipient updated

- Set the permanent owner notification recipient for website RFQs to
  `sanjit@growonlinetoday.com`; buyer confirmation emails remain unchanged.
- Updated the private Hostinger production configuration while preserving the
  SMTP sender mailbox, and verified the configured recipient without exposing
  credentials.
- Sent labelled production test `RFQ-RECIPIENT-VERIFY-20260725`; the endpoint
  accepted both the owner notification and buyer confirmation.

### 2026-07-25 — International Search Console connection completed

- Verified `sc-domain:urbanfreshrice.com` in the owner's correct Google account,
  `sanjit@growonlinetoday.com` (`/u/2`), through Cloudflare Domain Connect.
- Granted `seo-improver@ricemill-search.iam.gserviceaccount.com` Full access to
  the international property without exposing the copied credential.
- Successfully completed workflow `30167153921`: it matched the live sitemap to
  the repository, verified Search Console access and submitted
  `https://urbanfreshrice.com/sitemap.xml`. Search Console recorded the
  submission at `2026-07-25T17:12:15.415Z`.
- Confirmed that the homepage is indexed and that Google accepted priority
  indexing requests for the 1121, 1509, private-label and quality-testing
  landing pages.
- Reconfirmed the completed Ubersuggest audit at 100 health with all 11 pages
  successful and no errors, warnings or recommendations. The project tracks 10
  export-intent keywords weekly across the United States, United Kingdom and
  United Arab Emirates; none currently rank in the top 100.
- Confirmed the active dual-domain SEO automation remains scheduled for the
  first Monday of every month at 10:00 Asia/Kolkata.

### 2026-07-25 — Hostinger SMTP RFQ confirmations added

- Deployed a dedicated PHP endpoint at
  `https://email.urbanfreshrice.com/submit.php` on Hostinger Business Web
  Hosting, with the mailbox credential stored outside `public_html` and outside
  Git.
- Added authenticated Hostinger SMTP delivery through PHPMailer: one complete
  lead notification goes to the UrbanFresh mailbox and one branded
  acknowledgement goes to the buyer.
- Restricted browser access to the UrbanFresh production origins and added
  required-field and email validation, output escaping, a honeypot, IP-based
  rate limiting, generic public errors and private server logging.
- Made the buyer's business email required, connected the form to the verified
  SMTP endpoint, and retained the existing Google Sheets write as a secondary
  lead record.
- Verified HTTPS and CORS, sent a labelled two-message SMTP test successfully,
  and refreshed Hostinger's domain status to confirm MX, SPF, DKIM and DMARC
  are all correct.
- Published commit `662663c`; the live RFQ form loaded the versioned email
  integration, completed a production browser submission and reached the
  thank-you page. Hostinger's private rate log separately confirmed that the
  browser request reached the PHP endpoint.
- Rebuilt all 11 generated pages and passed the SEO audit, PHP syntax check,
  Composer validation, all 23 unit tests and `git diff --check`.

### 2026-07-25 — WhatsApp button alignment corrected

- Gave shared pill buttons an explicit 1.1 line height and supported 700 weight
  so Source Sans 3 is optically centred within the 50 px control.
- Excluded `.button` elements from the generic card-link weight rule that was
  overriding the intended CTA typography on the thank-you page.
- Bumped the generated stylesheet URL to `20260725-5` and added regression
  coverage for both declarations.

### 2026-07-25 — Impeccable responsive UI hardening completed

- Used the owner-supplied `Skill design/impeccable-main` audit, adapt and polish
  guidance as the quality standard for a full-site interface review.
- Added `PRODUCT.md` so future design work keeps the international buyer,
  specification-first purpose, factual boundaries and WCAG 2.2 AA target.
- Fixed the 320 px homepage headline clipping and product-table overflow,
  replaced the fragile mobile-menu offset, and rebuilt the thank-you page with
  reusable responsive components.
- Standardised 44 px interaction targets, keyboard focus, reduced motion,
  mobile safe areas and zero-min-width grid behavior across the shared system.
- Removed the detector-flagged side-stripe notice pattern and replaced the
  generic Inter declaration with the established UrbanFresh Bitter and Source
  Sans 3 typography system from the domestic site.
- Added four responsive regression tests and recorded the full evidence in
  `reports/ui-audit-2026-07-25.md`.
- Passed the SEO audit, all 19 unit tests, `git diff --check` and a rendered
  matrix of all 11 pages at 320, 375, 768, 1070 and 1440 px. All 55 cases had
  zero horizontal overflow, clipped visible elements, broken eager images or
  visible interaction targets below 44 by 44 px.
- Published commit `0eaffdc`; GitHub Pages deployment `30165799066` succeeded.
  Live checks confirmed stylesheet version `20260725-4`, the 1070 px thank-you
  layout, 320 px homepage and product table, 1440 px specification page,
  responsive navigation and zero horizontal overflow.

### 2026-07-25 — Hero photography and international SEO loop completed

- Fixed every hero image reference to use a root-relative path. The original
  relative path was resolving under `/assets/css/` and returning no photograph.
- Moved the collapsed-navigation breakpoint to 1120 px so the 1070 px layout
  shown in the owner screenshot cannot horizontally overflow or clip the hero.
- Published commit `c4908c4`; GitHub Pages deployment `30165238813` succeeded.
  Browser QA at 1070 px confirmed the mill photograph, complete headline,
  hamburger navigation, zero horizontal overflow and the correct live image
  URL.
- Copied the existing `GSC_CREDENTIALS_JSON` GitHub secret into this repository
  without exposing its value. Workflow `30165239202` verified that the live
  sitemap matches the repository, then stopped safely because the service
  account can currently see only `sc-domain:urbanfresh.in`.
- Created the active Ubersuggest project for `urbanfreshrice.com`, tracking ten
  export-intent keywords in the United States, United Kingdom and United Arab
  Emirates. The first audit crawled all 11 pages with a 100 health score, zero
  errors, zero warnings and zero recommendations.
- Expanded the existing Codex monthly SEO automation into the active
  `UrbanFresh Dual-Domain Monthly SEO Loop`. It runs on the first Monday of each
  month at 10:00 Asia/Kolkata and evaluates, validates and publishes each domain
  independently using its own Search Console property and Ubersuggest project.
- Rebuilt the generated pages, passed the local SEO audit, all 15 unit tests and
  `git diff --check`.

### 2026-07-25 — Source-grounded export launch build completed

- Created a separate export-site repository following the two-domain plan.
- Added a specification-first site architecture, copied first-party mill
  photography and transferred the proven local SEO/Search Console tooling.
- Used the existing `urbanfresh` repository as the factual source and omitted
  unsupported lab, port, container-load, MOQ and lead-time claims.
- Confirmed through Verisign RDAP that `urbanfreshrice.com` was registered on
  2026-07-25 with Cloudflare nameservers.
- Published commit `e59cade`, enabled GitHub Pages, confirmed the custom-domain
  certificate, enforced HTTPS, and verified the live homepage, sitemap,
  `robots.txt` and social-preview image returned HTTP 200.
- Verified the reciprocal About-page hreflang and the domestic-site
  International Buyers links live.

## Standard verification commands

```bash
python3 scripts/build_site.py
python3 scripts/seo_audit.py
python3 -m unittest discover -s tests -v
git diff --check
python3 scripts/submit_sitemap.py --dry-run
```
