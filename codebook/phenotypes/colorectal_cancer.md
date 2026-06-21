# Colorectal Cancer

Single source of truth for the Colorectal Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 200970, 4180790, 4180791, 4180792, 252658, 252946
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above (a single
  cancer diagnosis code is reliable).
- Hillsborough: TBD pending the health-survey instrument (map in `codebook/survey_variables.csv`).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported colorectal cancer).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Cancer phenotypes are sensitive to ascertainment; a single diagnosis code is usually reliable,
  which is why the cancers use >= 1 rather than the chronic-condition rule-of-two.
- Ascertainment differs by cohort (EHR vs survey self-report).
