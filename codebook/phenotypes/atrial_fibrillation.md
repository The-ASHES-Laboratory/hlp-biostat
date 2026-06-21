# Atrial Fibrillation

Single source of truth for the Atrial Fibrillation phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 313217, 313236, 312950, 4108832 (see `codebook/condition_concepts.csv`)
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
- Hillsborough: TBD (survey: no self-reported atrial fibrillation / irregular heartbeat).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4108832` is also listed under hypertension in `condition_concepts.csv`; resolve during
  phenotyping (see hypertension.md note).
- Atrial flutter vs fibrillation coding can vary; confirm the concept set captures the intended
  scope when the descendants decision is made.
- Ascertainment differs by cohort (EHR vs survey self-report).
