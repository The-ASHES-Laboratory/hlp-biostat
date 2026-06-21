# Prostate Cancer

Single source of truth for the Prostate Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 4163261, 4112853, 4119298, 4119601
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above.
- Hillsborough: TBD pending the health-survey instrument (map in `codebook/survey_variables.csv`).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- **Sex restriction (locked): male only.** Cases and controls restricted to `gender_concept_id`
  8507; female and unknown-sex participants are excluded. Hillsborough: same restriction.

## Exclusions
- Restrict to male participants (see Control definition).

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4112853` is ALSO listed under breast_cancer in `condition_concepts.csv`. One OMOP
  concept cannot be both prostate and breast cancer, so one is wrong. **Resolve before running
  associations** (likely a copy-paste; verify the concept's true meaning in OMOP/Athena).
- Prostate cancer in African American men has notably higher incidence and mortality, central to
  this study's disparities question; the sex restriction keeps controls at-risk.
- Ascertainment differs by cohort (EHR vs survey self-report).
