# Breast Cancer

Single source of truth for the Breast Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 4112853 (Malignant tumor of breast, standard); 4157332 (Malignant neoplasm of
  female breast, NON-standard - will not match `condition_concept_id`, map before use)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- **2026-06-22 QC:** removed `4155468` ("Mild asthma"), `4155469` ("Moderate asthma"),
  `4245676` ("Chemical-induced asthma") - all contamination, none breast cancer.
- **Effective set is one standard concept** (4112853). REBUILD (descendants / curated set, and
  map 4157332 to its standard form) before running associations.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above.
- Hillsborough: `diagnosed_cancer` == Yes AND `cancer_specify` matches breast -> case.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- **Sex restriction (locked): female only.** Cases and controls restricted to `gender_concept_id`
  8532 (male breast cancer excluded by this choice). Hillsborough: same restriction, BUT the
  Health Survey has no sex field - sex must come from UUID linkage to the master sheet.
- Hillsborough controls: `diagnosed_cancer` == No (other cancers excluded from controls).

## Exclusions
- Restrict to female participants.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Ascertainment differs by cohort (EHR vs survey self-report + free-text parse).
