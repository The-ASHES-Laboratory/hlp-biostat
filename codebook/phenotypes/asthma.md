# Asthma

Single source of truth for the Asthma phenotype. Both the AoU (national) and Hazel
(Hillsborough) pipelines build cases and controls from this definition via
`src/hlp/phenotypes.py`. Do not redefine it inside a notebook.

## OMOP condition concept set
- Concept IDs: 317009, 4051466, 257581, 256448 (see `codebook/condition_concepts.csv`)
- Match: exact `condition_concept_id` match. Descendants NOT expanded (as currently coded).
- Include descendants: no (current). **DECISION:** confirm whether to expand via the AoU
  concept-set tool; exact-match can miss child concepts coded in the EHR.

## Case definition
- AoU (national): >= 1 `condition_occurrence` record with a `condition_concept_id` in the set above.
  **DECISION:** keep >= 1 occurrence, or require >= 2 (rule-of-two) to cut EHR false positives?
- Hillsborough: TBD pending the health-survey instrument. Map the self-report item in
  `codebook/survey_variables.csv`, then fill here.

## Control definition
- AoU: cohort members with zero qualifying records. Cohort = `race_concept_id` in {8516, 8527}
  with genomic + EHR data.
- Hillsborough: TBD (survey: no self-reported asthma).

## Exclusions
- None specific. No sex restriction.

## Notes
- Comparison groups: African American (`race_concept_id` 8516) vs European American (8527).
- Asthma is often childhood-onset and may be resolved; a single historical EHR code does not
  distinguish active vs resolved disease. Relevant to the >= 1 vs >= 2 decision above.
- Ascertainment differs by cohort (EHR codes in AoU vs survey self-report in Hillsborough);
  account for this in the comparison.
