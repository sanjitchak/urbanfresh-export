# Codex automation: UrbanFresh weekly SEO monitor

- Stable ID: `urbanfresh-weekly-seo-monitor`
- Name: `UrbanFresh Weekly SEO Monitor`
- Schedule: every Monday at 09:00 in the project's local timezone
- Model: `gpt-5.6-sol`
- Reasoning effort: `medium`
- Execution: local, targeting the restored common parent project
- Path placeholder: replace `${RICE_BUSINESS_ROOT}` with the directory that
  contains the two cloned repositories.

## Prompt

Run the combined read-only weekly Search Console collector and SEO monitor for
both UrbanFresh domains:

- `${RICE_BUSINESS_ROOT}/urbanfresh` — `https://urbanfresh.in/`
- `${RICE_BUSINESS_ROOT}/urbanfresh-export` — `https://urbanfreshrice.com/`

Read each repository's `AGENTS.md`, `CHANGELOG.md` and applicable
content-verification rules first. Do not edit website content, commit, push,
submit sitemaps, request indexing, change Search Console/Ubersuggest settings,
add keywords or competitors, buy credits, or perform outreach. Never print or
expose credentials.

At the start of every run, generate the current dated Search Console report
independently for each repository with
`python3 scripts/seo_improver.py --report-date YYYY-MM-DD`. This automation is
the authoritative Monday collector; do not depend on a separate macOS
LaunchAgent. If one collector fails, continue safe read-only checks for the
other domain and report the failure. Run the local SEO audit and unit tests
read-only. Check the live homepage, `robots.txt` and `sitemap.xml` for HTTP
status, canonical host, accidental `noindex`, and sitemap/page parity. Inspect
the latest GitHub Actions quality/deployment/discovery status when available.

Read Ubersuggest project
`6e29c4c40a07eacf6f46cfce594ca5b745d1a6987745f6d3d6407dc79b679aa1`
for `urbanfresh.in` in India and project
`1c2848f9a84b8e6172b4f13915e7c287be5b99ae8dbfeacac40c84c59bade822`
for `urbanfreshrice.com` in the United States, United Kingdom and United Arab
Emirates. Treat Ubersuggest figures as estimates. Compare against the prior
weekly snapshot when one exists. For the international Search Console data,
report country/device separately and distinguish non-India discovery.

Write one concise dated snapshot outside both Git repositories at
`${RICE_BUSINESS_ROOT}/seo-monitor-reports/YYYY-MM-DD.md`. Highlight only
actionable changes: a new top-100 tracked keyword, a 10-or-more position
material decline among ranking terms, audit-score decline, new technical issue,
live noindex/canonical/robots/sitemap regression, failed workflow, collector
failure, or Search Console indexing/canonical regression. If none exists, say
both domains are healthy and include the small current baseline. This
automation diagnoses and reports only; it never modifies or publishes the
sites.
