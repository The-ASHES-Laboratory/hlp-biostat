# Colorectal Cancer

Single source of truth for the Colorectal Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 200970, 4180790, 4180791, 4180792, 252658, 252946 (see `codebook/condition_concepts.csv`)
- Match: exact `condition_concept_id` match. Descendants NOT expanded (as currently coded).
- Include descendants: no (current). **DECISION:** confirm whether to expand via the AoU
  concept-set tool; cancer subtypes are often coded as child concepts.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a `condition_concept_id` in the set above.
  **DECISION:** keep >= 1 occurrence, or require >= 2 (rule-of-two)?
- Hillsborough: TBD pending the health-survey instrument. Map the self-report item in
  `codebook/survey_variables.csv`, then fill here.

## Control definition
- AoU: cohort members with zero qualifying records. Cohort = `race_concept_id` in {8516, 8527}
  with genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported colorectal cancer).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Cancer phenotypes are sensitive to ascertainment: registry/EHR capture differs, and a single
  diagnosis code is usually reliable for a cancer (favoring the >= 1 occurrence rule).
- Ascertainment differs by cohort (EHR vs survey self-report).
