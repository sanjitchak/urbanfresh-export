# UrbanFresh schedule recovery

This directory is the Git-backed recovery source for the SEO schedules serving
both `urbanfresh.in` and `urbanfreshrice.com`. The same recovery pack is
mirrored in both repositories so one surviving clone is sufficient.

## What survives a computer failure

| Schedule | Runtime | When (Asia/Kolkata) | Recovery |
| --- | --- | --- | --- |
| Technical SEO quality, one per repo | GitHub Actions | Monday 09:00 | Already cloud-hosted |
| Two-domain report collector | macOS LaunchAgent | Monday 09:00 | Reinstall from the domestic repo |
| Read-only two-domain monitor | Codex on the local project | Monday 09:30 | Recreate from the versioned specification |
| Evidence-gated two-domain optimizer | Codex on the local project | First Monday 10:00 | Recreate from the versioned specification |

The technical GitHub schedules continue without the Mac. The Search Console
collector, LaunchAgent and Codex schedules are local services, so Git stores
their definitions but a new computer still needs a one-time restore. Search
Console report data is not uploaded to GitHub artifacts by this backup.

## Recovery on a new Mac

1. Clone `sanjitchak/urbanfresh` and `sanjitchak/urbanfresh-export` beside each
   other in one parent directory.
2. Restore the private `GSC_CREDENTIALS_JSON` value to each repo's ignored
   `.env.local`. Never commit that credential.
3. In the domestic repo, run:

   ```bash
   ./scripts/install_local_seo_schedule.sh
   ```

   This is the only LaunchAgent to install. Its runner already covers both
   domains; do not install a second copy from the export repo.
4. Open the common parent directory as a Codex project and ask Codex:
   `Restore the two UrbanFresh automations from both ops/schedules Codex
   specifications, using this project's current path and project ID.`
5. Confirm that the restored schedule list contains the stable IDs
   `urbanfresh-weekly-seo-monitor` and `urbanfresh-monthly-seo-loop`, once each.

## Private credential recovery

Encrypted secrets are intentionally not stored in Git. Keep the service-account
credential in a separate password manager or encrypted backup. After restoring
the repositories, place `GSC_CREDENTIALS_JSON` in each ignored `.env.local` and,
if a repository was transferred or recreated, add it again under
**Settings → Secrets and variables → Actions** for the existing authenticated
sitemap workflow.
