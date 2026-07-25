# UrbanFresh Export SEO operating rules

Search Console is the first-party performance source. Ubersuggest may be used
for external market, competitor and SERP research.

## Pre-launch

- Keep every page `noindex,nofollow` and keep `robots.txt` blocked.
- Do not add `CNAME` or submit the sitemap.
- Complete `CONTENT-VERIFICATION.md`.
- Validate a coherent 6-to-8-page buyer journey before indexing.

## Months 1 to 6

The one-change-per-month rule is suspended only for publication of the initial
Tier 1 and Tier 2 export pages. It still applies to edits of already-published
pages. Once the core compliance and export-mechanics pages are live and
receiving impressions, return to one evidence-backed change per month.

## Ongoing safeguards

- Never publish invented specifications, certification scope, capacity, lab
  results, export history, ports, packing loads, prices or testimonials.
- Never build templated country pages without first-party market evidence.
- Use self-canonicals. Use hreflang only for genuine, reciprocal regional
  equivalents.
- Measure qualified export RFQs and orders, not traffic alone.

## Commands

```bash
python3 scripts/seo_improver.py
python3 scripts/submit_sitemap.py --dry-run
```

After domain verification and launch approval, configure the Search Console
domain property `sc-domain:urbanfreshrice.com` and the repository secret
`GSC_CREDENTIALS_JSON`.

