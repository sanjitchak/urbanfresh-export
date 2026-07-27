# Codex automation: UrbanFresh monthly SEO loop

- Stable ID: `urbanfresh-monthly-seo-loop`
- Name: `UrbanFresh Dual-Domain Monthly SEO Loop`
- Schedule: first Monday of every month at 10:00 in the project's local timezone
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Execution: local, targeting the restored common parent project
- Path placeholder: replace `${RICE_BUSINESS_ROOT}` with the directory that
  contains the two cloned repositories.

## Prompt

Run the monthly evidence-led SEO loop for both UrbanFresh repositories:

- Domestic: `${RICE_BUSINESS_ROOT}/urbanfresh` (`https://urbanfresh.in/`)
- International: `${RICE_BUSINESS_ROOT}/urbanfresh-export`
  (`https://urbanfreshrice.com/`)

Before acting, read each repository's `AGENTS.md`, `CHANGELOG.md` and
content-verification rules completely. Treat each repository as an independent
site, property, report set, worktree and deployment. Preserve all user-owned
unrelated files and never stage, delete or overwrite them. If either repository
has unrelated tracked changes, do not touch that repository, but continue
safely with the other and report the blocker.

For each eligible repository: fetch origin, use `main`, and update only with
`git pull --ff-only`. Never stash, reset, force-push, expose secrets or print
`.env.local`. Run `python3 scripts/seo_improver.py` and compare the newest and
prior reports, keyword map, monthly log and previous experiment. Use that
domain's Google Search Console property as first-party truth. Require a full
comparable 28-day period before changing content. For `urbanfreshrice.com`,
preserve and report country/device dimensions separately, highlighting United
States, United Kingdom, United Arab Emirates and non-India performance rather
than merging markets. Use the exact matching Ubersuggest project as secondary
research: project
`6e29c4c40a07eacf6f46cfce594ca5b745d1a6987745f6d3d6407dc79b679aa1`
for `urbanfresh.in` and project
`1c2848f9a84b8e6172b4f13915e7c287be5b99ae8dbfeacac40c84c59bade822`
for `urbanfreshrice.com`. Keep Search Console facts separate from Ubersuggest
estimates and save a concise `external-research.md` in the dated ignored report
directory. Never buy credits, change billing, auto-add suggested
keywords/competitors, or perform automated backlink outreach.

Evaluate the prior logged change. Keep it when improved, revert only the exact
attributable prior SEO change when comparable evidence clearly worsened, and
make no change when evidence is inconclusive or sample size is weak. Choose at
most one reversible existing-page improvement per domain, and only when
first-party evidence supports the intent with a meaningful sample. Never invent
certifications, lab results, residue limits, export history, ports, packing or
container configurations, MOQ, lead time, capacity, prices, clients or
testimonials. Do not create net-new pages, doorway pages, mass content,
backlinks, reviews or spam. Keep design, forms, navigation, URLs and business
voice intact. For the international site, obey `CONTENT-VERIFICATION.md` and do
not add unsupported export claims.

Append no more than one row per domain and review date to
`seo/monthly-log.csv`, including a truthful
`No change - insufficient evidence` outcome when applicable. Record the
deployment SHA, exact page/query/country/device baseline, review date and
outcome when those fields are available. Update each touched `CHANGELOG.md`
with evidence, validation, publication/submission status and open items, never
credentials.

Validate each touched repository with its generator,
`python3 scripts/seo_audit.py`, `python3 -m unittest discover -s tests -v` and
`git diff --check`. Inspect scope. If validation passes and a valid diff exists,
commit that repository separately with a message beginning `Monthly SEO:` and
push `main` without force. Wait for the corresponding GitHub quality, Pages
deployment and post-deployment discovery workflows. Then verify the live
canonical page and run `python3 scripts/submit_sitemap.py --wait-for-live
--verify` plus `python3 scripts/submit_indexnow.py --wait-for-key`. If there is
no diff, do not create an empty commit or resubmit unchanged discovery files.
Report Search Console evidence, Ubersuggest evidence, country/device evidence
for the international site, decision, files, validation, commit/push, live
verification, sitemap result and IndexNow result separately for both domains.
