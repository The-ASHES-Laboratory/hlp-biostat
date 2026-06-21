# Prostate Cancer

Single source of truth for the Prostate Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 4163261, 4112853, 4119298, 4119601 (see `codebook/condition_concepts.csv`)
- Match: exact `condition_concept_id` match. Descendants NOT expanded (as currently coded).
- Include descendants: no (current). **DECISION:** confirm whether to expand via the AoU
  concept-set tool.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a `condition_concept_id` in the set above.
  **DECISION:** keep >= 1 occurrence, or require >= 2 (rule-of-two)?
- Hillsborough: TBD pending the health-survey instrument. Map the self-report item in
  `codebook/survey_variables.csv`, then fill here.

## Control definition
- AoU: cohort members with zero qualifying records. Cohort = `race_concept_id` in {8516, 8527}
  with genomic + EHR data.
- **Sex restriction (DECISION):** prostate cancer is male-only. Recommended: restrict BOTH cases
  and controls to males (`gender_concept_id` 8507) so controls are at-risk. The current notebook
  does NOT restrict by sex; this should change here. Hillsborough: same restriction.

## Exclusions
- Restrict to male participants (see Control definition). Exclude female and unknown-sex.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4112853` is ALSO listed under breast_cancer in `condition_concepts.csv`. One OMOP
  concept cannot be both prostate and breast cancer, so one of the two is wrong. **Resolve before
  building cases** (likely a copy-paste; verify the concept's true meaning in OMOP/Athena).
- Prostate cancer in African American men has notably higher incidence and mortality, central to
  this study's disparities question; sex restriction and concept accuracy matter here.
- Ascertainment differs by cohort (EHR vs survey self-report).
