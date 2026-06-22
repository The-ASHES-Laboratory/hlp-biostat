# Asthma

Single source of truth for the Asthma phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set (AoU)
- Concept IDs: 317009 (Asthma), 4051466 (Childhood asthma), 257581 (Acute asthma),
  256448 (Chronic asthmatic bronchitis)
- Matching: exact `condition_concept_id` match (locked). Descendant expansion not enabled.
- 2026-06-22 QC: this was the ONLY phenotype whose original concept set was fully correct
  (all 4 verified standard asthma concepts).

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two for chronic conditions).
- Hillsborough: `diagnosed_respiratoryissues` == Yes -> case; == No -> control;
  Unsure / Prefer-not-to-answer -> missing.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: `diagnosed_respiratoryissues` == No.

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- **Ascertainment caveat:** the Hillsborough item asks "asthma OR other respiratory issues", so it
  over-ascertains asthma relative to the AoU asthma-specific concept set. Interpret the
  cross-cohort comparison with this mismatch in mind.
