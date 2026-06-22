# Hypertension

Single source of truth for the Hypertension phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 316866 (Hypertensive disorder), 320128 (Essential hypertension)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- 2026-06-22 QC: removed `314754` ("Wheezing", a respiratory finding) - it was contamination,
  not a hypertension concept. Set verified against OHDSI Atlas.

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two for chronic conditions).
- Hillsborough: `diagnosed_highbloodpressure` == Yes -> case; == No -> control;
  Unsure / Prefer-not-to-answer -> missing. **Direct self-report match** (best of the six).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: `diagnosed_highbloodpressure` == No.

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Ascertainment differs by cohort: EHR codes (AoU) vs single self-report item (Hillsborough).
  This is the one phenotype where the two cohorts align cleanly.
