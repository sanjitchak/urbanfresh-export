# UrbanFresh Export project handoff

## Current state

- Repository: `sanjitchak/urbanfresh-export`, default branch `main`
- Intended production domain: `https://urbanfreshrice.com/`
- Site state: source-grounded launch build; DNS/HTTPS and Pages verification pending
- Domestic website: `https://urbanfresh.in/`
- Search Console property planned: `sc-domain:urbanfreshrice.com`

## Open items

- Verify GitHub Pages, DNS and HTTPS for `urbanfreshrice.com`.
- Add the Search Console domain property and grant the service account Full
  access after domain verification.
- Add the `GSC_CREDENTIALS_JSON` repository secret only after launch approval.
- Enable GitHub Pages and add `CNAME` only when the protected draft is approved.
- Add reciprocal `.in`/`.com` hreflang only for genuine equivalent pages.

## Change history

### 2026-07-25 — Source-grounded export launch build completed

- Created a separate export-site repository following the two-domain plan.
- Added a specification-first site architecture, copied first-party mill
  photography and transferred the proven local SEO/Search Console tooling.
- Used the existing `urbanfresh` repository as the factual source and omitted
  unsupported lab, port, container-load, MOQ and lead-time claims.
- Confirmed through Verisign RDAP that `urbanfreshrice.com` was registered on
  2026-07-25 with Cloudflare nameservers.

## Standard verification commands

```bash
python3 scripts/build_site.py
python3 scripts/seo_audit.py
python3 -m unittest discover -s tests -v
git diff --check
python3 scripts/submit_sitemap.py --dry-run
```
