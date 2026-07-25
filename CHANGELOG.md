# UrbanFresh Export project handoff

## Current state

- Repository: `sanjitchak/urbanfresh-export`, default branch `main`
- Intended production domain: `https://urbanfreshrice.com/`
- Production site: `https://urbanfreshrice.com/`
- Deployment: GitHub Pages from `main`; HTTPS enforced
- Domestic website: `https://urbanfresh.in/`
- Search Console property planned: `sc-domain:urbanfreshrice.com`

## Open items

- Add and verify the `sc-domain:urbanfreshrice.com` Search Console property,
  then grant `seo-improver@ricemill-search.iam.gserviceaccount.com` Full access.
- Rerun the sitemap workflow after Google exposes the property to that service
  account. The repository secret is already configured.

## Change history

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
