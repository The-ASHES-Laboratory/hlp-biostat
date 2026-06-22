# hlp-biostat Roadmap

Scientific milestones for the biostatistical component. Progress is tracked here plus git history.
Lightweight by design: update statuses as work lands.

Status key: `[ ]` not started, `[~]` in progress, `[x]` done.

## Milestone 0: Repository setup
- [x] Directory scaffold, governance, README, private GitHub repo
- [x] Pre-commit notebook-output stripping verified working

## Milestone 1: AoU Legacy -> Researcher Workbench 2.0 migration
One-way, irreversible mirror. Do it carefully.
- [x] Build migration runbook at `docs/migration-aou-2.0.md` from official AoU docs
- [x] Inventory legacy workspace (notebooks, buckets, datasets, config) before migrating
  (`docs/migration-inventory.md`; in-cloud read-only pass done. Notebook is self-contained;
  point-and-click objects do not block migration)
- [~] Execute migration following the runbook
  (2026-06-22: Carter's attempts failed - button reverts to "Retry" / hangs on "STARTING", never
  surfaces in 2.0 after 30+ min. Diagnosed as owner-role propagation lag: Carter was promoted to
  owner the same day, and the platform warns billing-pod/permission changes take 12-24h. Pivoting
  to Jalen (original Creator, no lag) to initiate; or Carter retries after 12-24h. Decided to
  re-run fresh in 2.0 rather than rescue the stale persistent-disk `merged_df`.)
- [ ] Verify all artifacts present in 2.0; confirm nothing was lost
  (Run the Validate check ~30 min post-start; capture RW 2.0 WORKSPACE_CDR / CDR_STORAGE_PATH.
  Do NOT delete the legacy workspace until 2.0 is validated and the analysis re-runs cleanly.)

## Milestone 2: Codebook
- [~] Define the 6 phenotypes in `codebook/phenotypes/` (OMOP concept sets + survey/EHR logic)
  (Case rule, sex restriction, and BOTH cohort halves now written. AoU notebook loads defs from
  the codebook via hlp. **BLOCKER: AoU concept sets were badly contaminated** - audit removed 11
  wrong IDs (mostly asthma misfiled under cancers/AF); cancer/AF/HTN sets are now thin and need a
  proper REBUILD before Milestone 3. Hillsborough: hypertension direct, asthma over-broad, cancers
  need free-text parse, AF not ascertainable from the survey.)
- [x] Map AoU survey variables and lifestyle variables to plain meanings
  (`survey_variables.csv` + `lifestyle_variables.csv` from the Hillsborough Health Survey codebook;
  metadata only, no PII. AoU side uses dynamic CDR queries, not a static variable list.)
- [x] Implement `src/hlp/phenotypes.py` to build cases/controls from the definitions
  (pure-Python core + pandas wrappers; reads condition_concepts.csv + phenotype_params.csv;
  7 unit tests passing. Pandas wrappers pending validation on real cohort data)

## Milestone 3: National cohort analysis (AoU)
- [ ] Build national AA cohort + extract phenotypes in the cloud
- [ ] Pull genomic data (exome / microarray PLINK)
- [ ] QC and association analysis for the 6 conditions

## Milestone 4: Hillsborough cohort analysis (Hazel)
- [ ] Genotype QC for the 62 participants
- [ ] Phenotype the cohort from survey data using the same definitions
- [ ] Association / risk analysis

## Milestone 5: Cohort comparison
- [ ] Compare Hillsborough vs national AA risk/prevalence for the 6 conditions
- [ ] Integrate lifestyle factors
- [ ] Figures + manuscript draft
