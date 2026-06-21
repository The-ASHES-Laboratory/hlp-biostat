# Asthma

Single source of truth for the Asthma phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook. Machine-readable encoding:
concept set in `codebook/condition_concepts.csv`, case rule in `codebook/phenotype_params.csv`.

## OMOP condition concept set
- Concept IDs: 317009, 4051466, 257581, 256448
- Matching: exact `condition_concept_id` match (locked). Descendant expansion is a forward hook
  in `phenotypes.py`, not enabled (needs the in-cloud `concept_ancestor` table).

## Case definition
- AoU (national): >= 2 `condition_occurrence` records on **distinct days** with a concept in the
  set above (rule-of-two, chosen for chronic conditions to cut EHR false positives).
- Hillsborough: TBD pending the health-survey instrument. Map the self-report item in
  `codebook/survey_variables.csv`, then fill here.

## Control definition
- AoU: cohort members not meeting the case rule. Cohort = `race_concept_id` in {8516, 8527} with
  genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported asthma).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Asthma is often childhood-onset and may be resolved; the rule-of-two reduces counting a single
  stray historical code as active disease.
- Ascertainment differs by cohort (EHR codes in AoU vs survey self-report in Hillsborough).
