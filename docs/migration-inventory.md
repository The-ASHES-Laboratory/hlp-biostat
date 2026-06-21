# Pre-Migration Inventory: AoU national-cohort workspace

*Derived from the local mirror `aou/HLP_project.ipynb` on 2026-06-20, plus a read-only
in-cloud pass (Carter, Reader role). Companion to `docs/migration-aou-2.0.md`. The Owner-only
execution packet is `docs/migration-handoff-owner.md`.*

This is the "inventory legacy workspace" step. It records what the local code reveals so the
irreversible in-cloud steps are fast and safe.

## Confirmed workspace facts (in-cloud, read-only)

| Field | Value |
|-------|-------|
| Workspace | Hillsborough Statistical Genetics Legacy Project (namespace aou-rw-1fda26b2) |
| Bucket | gs://fc-secure-0a7bd839-5651-4908-8d88-7f466ef6fb94 |
| Google project | terra-vpc-sc-3d95f7cd |
| CDR version | v8 (eligible) |
| Owner / Writer / Reader | jfrank@ / avicenti@ / cclinton@ |
| Billing | Initial credits show "expiring Feb 17, 2026" (already past) -> needs a valid billing source + active RW 2.0 pod before migrating |

**Role consequence:** Carter is a Reader. Migration, the writable terminal, and the
persistent-disk copy are Owner-only (Jalen). See `docs/migration-handoff-owner.md`.

## Point-and-click objects exist, but the notebook does not depend on them

The workspace has three GUI-built objects (all by jfrank@) that do NOT migrate:
- Cohort "Statistical Genetics Cohort"
- Concept Set "Statistical Genetics Conditions of Interest"
- Dataset "HLP_Dataset"

Reconciliation against the notebook: `HLP_project.ipynb` contains the **materialized SQL** these
objects generated (inline `cb_search_person`/`cb_search_all_events` subqueries, `concept_id IN
(...)` lists; no `cohort_definition_id` reference). The notebook is self-contained and will run
after migration without recreating the GUI objects. The concept-set logic is captured in
`codebook/condition_concepts.csv`. Recreating the GUI objects in 2.0 is optional (only for future
Data Explorer editing). **This de-risks the migration substantially.**

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

## [cloud] Status of in-cloud confirmations

- [x] Point-and-click objects identified (Cohort, Concept Set, Dataset). Confirmed the notebook
      does not depend on them; concept-set logic captured in `codebook/condition_concepts.csv`.
- [x] CDR version confirmed v8.
- [x] Access requirements current (RCR, Controlled Tier, DUCC all completed Oct 1, 2025).
- [~] Billing: credits appear expired (Feb 17, 2026). Needs valid billing source + active RW 2.0
      pod confirmed by Owner. **Gate 1 in the Owner packet.**
- [ ] [Owner] `HLP_project.ipynb` and any other scripts confirmed in the BUCKET (not only on PD).
- [ ] [Owner] Persistent-disk `merged_df` size checked; copied to bucket or chosen to discard.
- [ ] [Owner] Verily Terms of Service accepted in RW 2.0.
- [ ] [Owner] Confirm this is the only AoU workspace needing migration.

## Codebook capture note

Per the runbook, any logic that does not migrate (point-and-click objects, ad hoc cohort criteria)
should be written into `codebook/` so the analysis stays reproducible regardless of platform. None
identified from the local code yet; revisit after the [cloud] checks above.
