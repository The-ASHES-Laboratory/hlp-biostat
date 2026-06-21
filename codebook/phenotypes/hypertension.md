# Hypertension

Single source of truth for the Hypertension phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 316866, 314754, 320128
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two for chronic conditions).
- Hillsborough: TBD pending the health-survey instrument (map in `codebook/survey_variables.csv`).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported high blood pressure).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4108832` (SNOMED 195080001 "Atrial fibrillation and flutter") was removed from this set
  on 2026-06-20: it is a cardiac-arrhythmia concept that was mis-included here. It now lives only
  in atrial_fibrillation.
- Hypertension is high-prevalence; medication (drug_exposure) or BP measurements could supplement
  condition codes in future, not currently used.
- Ascertainment differs by cohort (EHR vs survey self-report).
