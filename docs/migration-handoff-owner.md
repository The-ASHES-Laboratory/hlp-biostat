# Owner Green-Light Packet: AoU Workspace Migration

*For Jalen Franklin (`jfrank@researchallofus.org`), workspace Owner. Companion to
`docs/migration-aou-2.0.md` (full runbook) and `docs/migration-inventory.md` (inventory).
Prepared 2026-06-20. Migration deadline: June 30, 2026.*

Only the **Owner/Creator** can run the migration, the writable terminal, and the
persistent-disk copy. Carter is a Reader, so this is yours to execute. Everything below is
prepped so you can move fast and safe.

## Workspace identity (confirm this is the one)

| Field | Value |
|-------|-------|
| Workspace name | Hillsborough Statistical Genetics Legacy Project |
| Namespace | aou-rw-1fda26b2 |
| Bucket | gs://fc-secure-0a7bd839-5651-4908-8d88-7f466ef6fb94 |
| Google project | terra-vpc-sc-3d95f7cd |
| CDR version | v8 (eligible) |
| Owner | jfrank@ &nbsp;|&nbsp; Writer: avicenti@ &nbsp;|&nbsp; Reader: cclinton@ |

> Note: the workspace is named "Hillsborough ... Legacy" but the code in it pulls the
> **national All of Us** cohort (it queries the CDR directly). Confirm this is the workspace
> that holds the national-cohort analysis and that no second AoU workspace also needs migrating.

## The good news (this is low-risk)

The analysis notebook `HLP_project.ipynb` is **self-contained**. The point-and-click objects
you built (Cohort "Statistical Genetics Cohort", Concept Set "Statistical Genetics Conditions
of Interest", Dataset "HLP_Dataset") were just the authoring tools. Their logic is already
baked into the notebook as inline SQL (`cb_search_person` subqueries, `concept_id IN (...)`
lists), and the notebook lives in the bucket, so **it migrates and will still run**. You do
NOT need to recreate those three objects for the notebook to work; recreating them is only
useful if you want to keep editing via the Data Explorer GUI later.

The concept-set logic is also now captured in the repo at `codebook/condition_concepts.csv`,
so it cannot be lost.

## Two real gates before you press the button

### Gate 1 — Billing (likely the blocker)
The legacy workspace shows initial credits "expiring Feb 17, 2026," which is already past.
Runbook Step 1 requires a **valid billing account** linked to the legacy workspace AND an
**active billing pod in Researcher Workbench 2.0** (a newly added pod can take up to 24h to
appear). Sort this first or the migration will not start.
- [ ] Valid billing source linked (GCP billing account, since initial credits look expired).
- [ ] Active billing pod exists in RW 2.0. Note its name; you select it during migration.

### Gate 2 — Persistent-disk outputs (your decision)
The notebook writes outputs to a relative path `merged_df/` = the **persistent disk**, which is
**NOT migrated**. Contents: cohort CSVs, PLINK phenotype/covariate files, batch results,
checkpoints. These are regenerable by re-running the notebook in 2.0.
- [ ] Decide: preserve or re-run fresh.
- [ ] If preserving, from the legacy Jupyter terminal:
  ```bash
  du -sh merged_df                                   # see what's there
  gsutil -m cp -r merged_df ${WORKSPACE_BUCKET}/merged_df
  gsutil ls -l ${WORKSPACE_BUCKET}/merged_df          # confirm it landed
  ```
  Confirm the bucket file count matches the local folder before migrating.

## Migrate (only when both gates are clear)

From the LEGACY Workbench (https://workbench.researchallofus.org/login):
1. [ ] "Go to workspaces" -> open "Hillsborough Statistical Genetics Legacy Project".
2. [ ] Workspace **Data tab** -> review eligibility checks. All must be green. If any fails, stop.
3. [ ] "Get Started".
4. [ ] Select the **RW 2.0 billing pod** (from Gate 1).
5. [ ] "Start migration". The workspace may be briefly unavailable; no further action needed.

## Validate in RW 2.0 (~30+ min after)
- [ ] Open migrated workspace (same title) in the Workspaces tab. Wait >=30 min before creating
      an analysis environment.
- [ ] Resources tab -> Browse: confirm files under the auto-mounted `workspace` bucket in a
      folder `rw-migration-aou-rw-XXXXXXXX`. Confirm `HLP_project.ipynb` and (if copied)
      `merged_df/` are present.
- [ ] Report back to Carter: the 2.0 values of `WORKSPACE_CDR` and `CDR_STORAGE_PATH`, and the
      confirmed CDR version. Carter needs these to resolve the v7/v8 genomic-path mismatch and
      update the notebook in the repo (runbook Step 4).
- [ ] Do NOT re-run the analysis or recreate cohorts yet; Carter handles the code-reference
      updates in the repo first.

## After validation
- [ ] Work only in 2.0 from here. Do not keep editing legacy (re-syncing overwrites migrated files).
- [ ] Once 2.0 is confirmed working, consider deleting the legacy workspace to stop storage charges.

## GREEN LIGHT checklist (all true = press the button)
- [ ] Confirmed this is the correct/only AoU workspace to migrate.
- [ ] Gate 1: valid billing linked + active RW 2.0 pod (name in hand).
- [ ] Gate 2: `merged_df` copied to bucket, or consciously chosen to discard.
- [ ] You are signed in as Owner (jfrank@).
- [ ] Collaborators (avicenti@, cclinton@) informed migration is happening.
