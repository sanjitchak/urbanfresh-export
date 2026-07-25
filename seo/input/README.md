# Search Console CSV fallback

The local SEO improver can use CSV exports without any API credentials.

In Google Search Console, set the date comparison to the latest complete 28 days versus the previous 28 days, open the **Queries** table and export CSV. Save the files locally as:

- `seo/input/current.csv`
- `seo/input/previous.csv`

Those filenames are gitignored because Search Console performance data should not be published accidentally.

Run:

```bash
python3 scripts/seo_improver.py \
  --current-csv seo/input/current.csv \
  --previous-csv seo/input/previous.csv
```

Supported headers include `Query` or `Top queries`, `Clicks`, `Impressions`, `CTR`, `Position`, and an optional `Page` column. Cannibalization detection needs query-and-page rows, which the API mode supplies automatically.
