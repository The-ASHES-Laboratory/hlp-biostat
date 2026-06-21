# Breast Cancer

Single source of truth for the Breast Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 4112853, 4155468, 4155469, 4157332, 4245676 (see `codebook/condition_concepts.csv`)
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
- **Sex restriction (DECISION):** breast cancer is overwhelmingly female; male breast cancer is
  rare. Recommended: restrict cases and controls to females (`gender_concept_id` 8532), or
  explicitly decide to include male breast cancer. The current notebook does NOT restrict by sex.
  Hillsborough: same restriction.

## Exclusions
- Restrict by sex per the Control-definition decision above.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Concept `4112853` is ALSO listed under prostate_cancer in `condition_concepts.csv`. One OMOP
  concept cannot be both, so this set likely contains a wrong ID. **Resolve before building cases**
  (verify `4112853`'s true meaning in OMOP/Athena; it is probably a prostate concept mis-pasted
  here).
- Ascertainment differs by cohort (EHR vs survey self-report).
