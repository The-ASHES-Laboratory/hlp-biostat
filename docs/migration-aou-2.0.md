# Runbook: AoU Legacy Workbench -> Researcher Workbench 2.0 Migration

*Source: All of Us official guide, "Migrating Workspaces from Legacy Workbench to Researcher
Workbench 2.0" (support.researchallofus.org, article 48266066855188). Captured 2026-06-20.*

## TL;DR for this project

- **Deadline: June 30, 2026.** Unmigrated workspaces are auto-archived (recoverable during a
  retention period), not immediately deleted. Migrate before then to avoid restoration delays.
- Migration is **not** a destroy-legacy operation. The legacy workspace stays accessible and is
  NOT locked after migration. You can even re-sync (but re-syncing overwrites the earlier
  migrated files). After migrating, work only in 2.0 to avoid override confusion.
- The only genuinely irreversible-loss risks, and the whole reason to be careful:
  1. **Persistent-disk files are not migrated.** Move them to the workspace bucket first.
  2. **Point-and-click cohorts / datasets / concept sets are not migrated.** Record their logic.
     Code-based Cohort/Dataset Builder queries saved inside notebooks DO migrate (they live in
     the bucket).
- Our workspace uses **CDR v8** (notebook references `gs://fc-aou-datasets-controlled/v8/...`),
  so it is eligible. Queries are code-based in `HLP_project.ipynb`, so they travel with the bucket.

## What migrates vs what does not

| Item | Migrated? | Action |
|------|-----------|--------|
| Files in the workspace bucket (incl. notebooks, scripts, saved queries) | Yes | Confirm everything is in the bucket |
| Workspace metadata + access policies | Yes | None |
| Persistent-disk files | **No** | Move to bucket BEFORE migrating, or they're left behind |
| Point-and-click cohorts, datasets, concept sets | **No** | Record logic; recreate in 2.0 Data Explorer |
| Custom Python/R packages | No | Reinstall in 2.0 |
| Environment variables / setup | No | Reconfigure in 2.0 |

---

## Step 1: Confirm eligibility and access (pre-migration)

- [ ] Annual All of Us data access requirements current: RCR refresher modules done, Data User
      Code of Conduct re-attested, contact info / institutional affiliation confirmed.
- [ ] Logged into Researcher Workbench 2.0 at least once and accepted the **Verily Terms of
      Service** (required to create/manage 2.0 workspaces).
- [ ] Legacy workspace linked to a valid billing account (All of Us initial credits if not
      expired/exhausted, OR a GCP billing account).
- [ ] An **active billing pod** exists in Researcher Workbench 2.0 (newly added pods can take up
      to 24 h to appear).
- [ ] Confirm you are the workspace **Owner or Creator** (only they can initiate migration).
      Coordinate with collaborators first; after migration all collaborators see a "Migrated" tag.

## Step 2: Prepare and clean up the workspace (pre-migration)

- [ ] **CDR version is v7 or v8.** (Ours is v8: eligible.) v3-v6 workspaces must be duplicated and
      upgraded to v7/v8 first, or they will not migrate.
- [ ] **Move all persistent-disk files into the workspace bucket.** Check via the Jupyter icon
      pop-up: a blue "DELETE PERSISTENT DISK" option means a PD is active. To delete a PD you must
      first stop/delete the running cloud environment. Use `gsutil`/`gc_data_storage` to copy PD
      files to the bucket.
- [ ] **Record cohort / dataset / concept-set logic** for anything built with the point-and-click
      tools: inclusion/exclusion criteria, concept definitions, and logic. These do NOT migrate.
      (Our analysis is code-based in the notebook, so confirm nothing critical exists only as a
      saved point-and-click object.)
- [ ] Review and categorize workspaces (migrate / archive / delete). Consolidate split work if
      helpful. Delete test-only cohorts, concept sets, datasets, notebooks to cut storage cost.
- [ ] Confirm `HLP_project.ipynb` and any other needed scripts are saved in the **workspace
      bucket** (not only on a persistent disk).

## Step 3: Migrate (the actual migration)

> Initiated from the LEGACY Workbench. Owner/Creator only.

1. [ ] Log into legacy Workbench: https://workbench.researchallofus.org/login
2. [ ] On the landing page, select **"Go to workspaces."**
3. [ ] Select the Researcher Workbench 1.0 workspace to migrate (you'll be prompted to begin).
4. [ ] Under the workspace **"Data" tab**, review eligibility checks + guidance, then select
       **"Get Started."**
5. [ ] Select the **billing pod** for Researcher Workbench 2.0 to use.
6. [ ] Select **"Start migration."**

Automated process then: creates a new RW 2.0 workspace, transfers all bucket files, copies
metadata and access policies. No further action needed during migration; the workspace may be
temporarily unavailable. Duration scales with workspace size.

## Step 4: Validate in Researcher Workbench 2.0 (post-migration)

- [ ] Open the migrated workspace in RW 2.0 (Workspaces tab; same title as in 1.0).
- [ ] **Wait up to 30 minutes** for GCS bucket contents to populate; wait at least 30 minutes
      before creating an app/analysis environment.
- [ ] In the **Resources tab**, select "Browse" and confirm files are present. Migrated bucket
      contents live under the auto-mounted bucket `workspace`, in a folder named
      `rw-migration-aou-rw-XXXXXXXX`.
- [ ] Verify notebooks, scripts, and data files open as expected (Jupyter File Management or
      `gsutil`).
- [ ] **Update SQL/CDR references in code.** Replace explicit RW 1.0 paths
      (e.g. `fc-aou-cdr-prod-ct.R2024Q3R8`) with the RW 2.0 equivalents
      (e.g. `wb-affable-acorn-7941.R2024Q3R9`); confirm exact references against Featured
      Workspaces. Re-check `CDR_STORAGE_PATH` / `GOOGLE_PROJECT` usage and the controlled-tier
      bucket paths in `HLP_project.ipynb`.
- [ ] Recreate any needed cohorts / datasets / concept sets using the **Data Explorer**.
- [ ] Reconfigure environment variables and reinstall any custom Python/R packages.
- [ ] Confirm the analysis runs end-to-end in RW 2.0.

## Step 5: After validation

- [ ] Once 2.0 is confirmed working, consider deleting the legacy 1.0 workspace to stop storage
      charges. Do NOT keep editing legacy: changes don't auto-sync, and re-syncing overwrites the
      migrated 2.0 files.
- [ ] Mirror any migrated/finalized analysis code back into this repo (`aou/`) so the canonical
      source of truth stays current.

## Notes specific to hlp-biostat

- This migration concerns only the **AoU national-cohort workspace**. The Hillsborough cohort
  data (Hazel + local survey) is unaffected.
- Keep this repo as the durable copy of the AoU analysis code: after the migration settles, pull
  the updated notebooks/scripts down into `aou/` and commit. Cohort/concept-set logic that does
  not migrate should be captured in `codebook/` so it is reproducible regardless of platform.
