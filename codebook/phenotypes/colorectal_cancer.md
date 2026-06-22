# Colorectal Cancer

Single source of truth for the Colorectal Cancer phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 4180790 (Malignant tumor of colon), 4180791 (Malignant tumor of hepatic flexure),
  4180792 (Malignant tumor of rectosigmoid junction)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- **2026-06-22 QC:** removed `200970` ("Carcinoma in situ of prostate"), `252658` ("Intrinsic
  asthma"), `252946` ("Coal workers' pneumoconiosis") - all contamination, none colorectal.
- **Set is thin (3 concepts)** after cleanup and almost certainly incomplete (no rectum/anus, no
  descendants). REBUILD with a proper colorectal-cancer concept set before running associations.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a concept in the set above.
- Hillsborough: `diagnosed_cancer` == Yes AND `cancer_specify` free text matches
  colorectal/colon/rectal -> case.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: `diagnosed_cancer` == No. Participants with a DIFFERENT cancer (Yes but specify
  not colorectal) are excluded from controls, not counted as controls.

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Hillsborough case-finding depends on free-text parsing of `cancer_specify`; spelling/format
  variation will need handling.
- Ascertainment differs by cohort (EHR vs survey self-report).
