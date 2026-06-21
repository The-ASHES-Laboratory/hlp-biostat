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
- [ ] Execute migration following the runbook
  (Owner-only; green-light packet ready at `docs/migration-handoff-owner.md`. Hand to jfrank@.
  Gates: billing pod + persistent-disk `merged_df` rescue)
- [ ] Verify all artifacts present in 2.0; confirm nothing was lost

## Milestone 2: Codebook
- [ ] Define the 6 phenotypes in `codebook/phenotypes/` (OMOP concept sets + survey/EHR logic)
- [ ] Map AoU survey variables and lifestyle variables to plain meanings
- [ ] Implement `src/hlp/phenotypes.py` to build cases/controls from the definitions

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
