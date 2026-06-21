# Hypertension

Single source of truth for the Hypertension phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 316866, 4108832, 314754, 320128 (see `codebook/condition_concepts.csv`)
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
- Hillsborough: TBD (survey: no self-reported high blood pressure).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4108832` is also listed under atrial_fibrillation in `condition_concepts.csv`. A single
  OMOP concept denotes one entity, so this is likely a copy-paste to resolve during phenotyping
  (it would double-count those participants as both HTN and AF cases).
- Hypertension is high-prevalence; consider whether medication (drug_exposure) or measurement
  (BP readings) should supplement the condition codes. Not currently used.
- Ascertainment differs by cohort (EHR vs survey self-report).
