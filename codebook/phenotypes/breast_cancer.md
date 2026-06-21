# Breast Cancer

Single source of truth for the Breast Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 4112853, 4155468, 4155469, 4157332, 4245676
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above.
- Hillsborough: TBD pending the health-survey instrument (map in `codebook/survey_variables.csv`).

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- **Sex restriction (locked): female only.** Cases and controls restricted to `gender_concept_id`
  8532; male and unknown-sex participants are excluded (male breast cancer is rare and excluded by
  this choice). Hillsborough: same restriction.

## Exclusions
- Restrict to female participants (see Control definition).

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4112853` is ALSO listed under prostate_cancer in `condition_concepts.csv`. One OMOP
  concept cannot be both, so this set likely contains a wrong ID. **Resolve before running
  associations** (verify `4112853` in OMOP/Athena; it is probably a prostate concept mis-pasted
  here, in which case it should be removed from this breast-cancer set).
- Ascertainment differs by cohort (EHR vs survey self-report).
