# Pre-Migration Inventory: AoU national-cohort workspace

*Derived from the local mirror `aou/HLP_project.ipynb` on 2026-06-20. Companion to
`docs/migration-aou-2.0.md`. Complete the in-cloud checks before clicking "Start migration".*

This is the "inventory legacy workspace" step. It records what the local code reveals so the
irreversible in-cloud steps are fast and safe. Items marked **[cloud]** can only be confirmed
inside the legacy Workbench.

## CRITICAL: persistent-disk outputs are not migrated

The notebook writes all outputs to a **relative** path, which is the persistent disk, not the
workspace bucket:

```
OUTPUT_DIR  = "merged_df"          # relative -> persistent disk
RESULTS_DIR = "merged_df/results"
PLINK_DIR   = "merged_df/plink_files"
BATCH_DIR   = "merged_df/batches"
checkpoint  = "merged_df/checkpoint.txt"
```

Files at risk (left behind unless copied to the bucket first):
- `results/african_american_cohort.csv`, `european_american_cohort.csv`, `prevalence_comparison.csv`
- `plink_files/phenotypes.txt`, `covariates.txt`, `plink_commands.sh`, SNP lists
- `batches/batch_NNN_results.csv`, analysis/conditions CSVs, `checkpoint.txt`

**Action before migrating (runbook Step 2):** from the legacy environment, copy the persistent-disk
outputs into the bucket, e.g.

```bash
gsutil -m cp -r merged_df ${WORKSPACE_BUCKET}/merged_df
gsutil ls ${WORKSPACE_BUCKET}/merged_df    # confirm
```

Decide first whether these regenerable outputs are worth preserving, or whether re-running in RW 2.0
is cleaner. If re-running: nothing to copy, but note that here so it is a decision, not an oversight.

## Environment variables the code depends on (reconfigure in 2.0)

Read dynamically, so no hardcoded values to rewrite, but the variables must exist in RW 2.0:

| Variable | Used for |
|----------|----------|
| `WORKSPACE_CDR` | CDR dataset for SQL/cohort queries |
| `CDR_STORAGE_PATH` | CDR storage root |
| `WORKSPACE_BUCKET` | bucket listing (and target for the copy above) |
| `GOOGLE_PROJECT` | `gsutil -u` requester-pays billing for controlled datasets |

These are auto-provided by the Workbench runtime. Confirm they resolve in 2.0 before re-running.

## Controlled-dataset genomic paths (confirm against RW 2.0 Featured Workspaces)

CDR-version-pinned; v8 is current and eligible:
- `gs://fc-aou-datasets-controlled/v7/wgs/`
- `gs://fc-aou-datasets-controlled/v8/exome/plink_bed/`
- `gs://fc-aou-datasets-controlled/v8/microarray/plink/arrays.*`
- `gs://fc-aou-datasets-controlled/v8/wgs/`

The notebook mixes v7 and v8 wgs paths. **Resolve to a single CDR version** in 2.0 to keep the
genomic pull consistent.

## Good news (less to do in Step 4)

- No hardcoded `fc-aou-cdr-prod-ct.R20XXQXRX` CDR references: queries use `WORKSPACE_CDR`, so the
  Step 4 SQL-rewrite is minimal.
- No `pip install` / `conda install` in the notebook: no custom packages to reinstall.
- Cohort/Dataset queries are code-based (in the notebook, in the bucket), so they migrate.

## [cloud] Still to confirm inside the legacy Workbench

- [ ] No point-and-click Cohorts / Datasets / Concept Sets exist that are NOT also expressed in code.
      If any do, record their inclusion/exclusion + concept logic into `codebook/` (they do not migrate).
- [ ] `HLP_project.ipynb` in the workspace bucket matches this repo's copy (the canonical source).
- [ ] No other notebooks/scripts live only on the persistent disk.
- [ ] Eligibility + access (runbook Step 1): RCR current, Verily ToS accepted, billing pod active,
      you are Owner/Creator.

## Codebook capture note

Per the runbook, any logic that does not migrate (point-and-click objects, ad hoc cohort criteria)
should be written into `codebook/` so the analysis stays reproducible regardless of platform. None
identified from the local code yet; revisit after the [cloud] checks above.
