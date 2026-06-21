# Atrial Fibrillation

Single source of truth for the Atrial Fibrillation phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 313217, 313236, 312950, 4108832
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two for chronic conditions).
- Hillsborough: TBD pending the health-survey instrument (map in `codebook/survey_variables.csv`).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported atrial fibrillation / irregular heartbeat).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4108832` is also listed under hypertension in `condition_concepts.csv`; resolve during
  Milestone 2 cleanup (see hypertension.md note).
- Atrial flutter vs fibrillation coding can vary; revisit the concept set if descendant expansion
  is enabled later.
- Ascertainment differs by cohort (EHR vs survey self-report).
