# urbanfresh-export

Export-focused website for UrbanFresh Rice Mills at `urbanfreshrice.com`.

This repository is intentionally separate from the domestic `urbanfresh.in`
website. The export site follows a specification-first buyer journey and must
not become a page-for-page copy of the domestic site.

## Source boundary

Business claims come from the existing `sanjitchak/urbanfresh` repository. When
that source does not name a lab, port, exact container load, MOQ or lead time,
this site does not invent one; it asks the buyer to confirm the requirement per
enquiry.

## Build and validate

```bash
python3 scripts/build_site.py
python3 scripts/seo_audit.py
python3 -m unittest discover -s tests -v
git diff --check
```
