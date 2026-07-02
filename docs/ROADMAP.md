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
- [x] Execute migration following the runbook
  (2026-06-30: Jalen made Carter co-owner; the owner-role propagation lag cleared and the
  migration to RW 2.0 completed successfully. Re-ran fresh in 2.0 rather than rescue the stale
  persistent-disk `merged_df`. Earlier 2026-06-22 attempts had stalled on "STARTING" / reverted
  to "Retry" due to same-day owner promotion, which is why Jalen initiated.)
- [~] Verify all artifacts present in 2.0; confirm nothing was lost
  (Validation in progress: run the Resources-tab file check ~30 min post-migration; capture RW 2.0
  WORKSPACE_CDR / CDR_STORAGE_PATH + CDR version. Do NOT delete the legacy workspace until 2.0 is
  validated and the analysis re-runs cleanly.)

## Milestone 2: Codebook
- [~] Define the 6 phenotypes in `codebook/phenotypes/` (OMOP concept sets + survey/EHR logic)
  (Case rule, sex restriction, and BOTH cohort halves now written. AoU notebook loads defs from
  the codebook via hlp. **BLOCKER: AoU concept sets were badly contaminated** - audit removed 11
  wrong IDs (mostly asthma misfiled under cancers/AF); cancer/AF/HTN sets are now thin and need a
  proper REBUILD before Milestone 3 - plan at `docs/concept-set-rebuild-plan.md` (do it in the AoU
  2.0 concept-set builder post-migration). Hillsborough: hypertension direct, asthma over-broad,
  cancers need free-text parse, AF not ascertainable from the survey.)
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
- [~] Association / risk analysis
  (`src/hlp/risk.py`: logistic risk models phenotype ~ lifestyle + demographics via statsmodels;
  adjusted odds ratios + 95% CIs + p-values, complete-case, small-n separation surfaced. 7 unit
  tests. Awaits labeled cohort. NOTE: n~62 will hit separation for rare phenotypes - watch it.)
- [~] Phenotype the cohort from survey data using the same definitions
  (`src/hlp/survey_phenotypes.py` implemented: survey -> case/control with the same 1/0/None
  contract as the AoU side, rules in `codebook/survey_rules.csv`. Direct (HTN, asthma),
  cancer free-text parse (colorectal/prostate/breast), AF dropped as not-ascertainable.
  Sex for prostate/breast resolved via `src/hlp/linkage.py` (attach_sex from the master-sheet
  UUID linkage; unknown sex -> excluded). 20 unit tests. Awaits the real survey extract + master
  sheet to run. Cancer keyword lists in survey_rules.csv are seeded defaults pending Carter's
  review.)
- [ ] Association / risk analysis

## Milestone 5: Cohort comparison
- [~] Compare Hillsborough vs national AA risk/prevalence for the 6 conditions
  (Comparison engine implemented: `src/hlp/compare.py` - prevalence + Fisher's exact between two
  groups, AA-vs-EA or Hillsborough-vs-national. Awaits real labeled cohorts to run.)
- [~] Integrate lifestyle factors
  (`src/hlp/lifestyle.py`: derives smoking status (never/former/current from the multi-select),
  alcohol/sleep ordinals, and gated exercise level from `lifestyle_variables.csv`. 9 unit tests.
  Diet/environment items deferred. ChewingTobacco counted as current tobacco use - flag for review.
  Feeds the risk models once the association module lands.)
- [ ] Figures + manuscript draft
