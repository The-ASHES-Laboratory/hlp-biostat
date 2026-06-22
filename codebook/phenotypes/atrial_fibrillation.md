# Atrial Fibrillation

Single source of truth for the Atrial Fibrillation phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 313217 (Atrial fibrillation, standard); 4108832 (Atrial fibrillation and flutter,
  NON-standard - will not match `condition_concept_id`; 313217 does the real matching)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- **2026-06-22 QC:** removed `313236` ("Cough variant asthma") and `312950` ("IgE-mediated
  allergic asthma") - both contamination, neither an arrhythmia.
- **Effective set is one standard concept** (313217). Consider descendants / a curated AF set
  before running associations.

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two for chronic conditions).
- Hillsborough: **NOT reliably ascertainable.** The survey has no AF-specific item; the closest is
  `diagnosed_cardiovascularcondition` ("heart disease or any cardiovascular condition"), which is
  any-CVD, not AF. Options: (a) treat Hillsborough AF as undefined and drop it from the
  cross-cohort comparison, or (b) use any-CVD as an explicitly-labeled broad proxy. Default: drop,
  to avoid a misleading comparison.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: undefined (see Case definition).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- **This is the weakest cross-cohort phenotype:** AF is well-defined in AoU (EHR) but not captured
  by the Hillsborough survey. Flag prominently in any cohort comparison.
