# UrbanFresh Export project handoff

## Current state

- Repository: `sanjitchak/urbanfresh-export`, default branch `main`
- Intended production domain: `https://urbanfreshrice.com/`
- Production site: `https://urbanfreshrice.com/`
- Deployment: GitHub Pages from `main`; HTTPS enforced
- Domestic website: `https://urbanfresh.in/`
- Search Console property planned: `sc-domain:urbanfreshrice.com`

## Open items

- Add the Search Console domain property and grant the service account Full
  access after domain verification.
- Add the existing `GSC_CREDENTIALS_JSON` credential to this repository after
  explicit approval; the first sitemap workflow failed safely because the
  secret is absent.

## Change history

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
