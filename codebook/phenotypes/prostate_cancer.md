# Prostate Cancer

Single source of truth for the Prostate Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 4163261 (Malignant tumor of prostate)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- **2026-06-22 QC:** removed `4119298` ("Late onset asthma") and `4119601` ("Lone atrial
  fibrillation") - both contamination, neither prostate.
- **Set is down to a single parent concept** after cleanup. With exact match it will miss specific
  prostate-cancer subtypes coded in the EHR. REBUILD (descendant expansion or a curated set)
  before running associations.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above.
- Hillsborough: `diagnosed_cancer` == Yes AND `cancer_specify` matches prostate -> case.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- **Sex restriction (locked): male only.** Cases and controls restricted to `gender_concept_id`
  8507. Hillsborough: same restriction, BUT the Health Survey has no sex field - sex must come
  from UUID linkage to the master sheet (see `data/README.md`).
- Hillsborough controls: `diagnosed_cancer` == No (other cancers excluded from controls).

## Exclusions
- Restrict to male participants.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Prostate cancer in African American men has notably higher incidence and mortality, central to
  this study's disparities question; the thin AoU concept set is a priority to rebuild.
- Ascertainment differs by cohort (EHR vs survey self-report + free-text parse).
