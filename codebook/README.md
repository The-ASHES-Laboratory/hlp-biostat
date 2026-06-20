# codebook/

The living data dictionary. This is a co-equal deliverable with the analysis pipeline, not an
afterthought. Keep it current as definitions evolve.

## Contents

| File | Purpose |
|------|---------|
| `survey_variables.csv` | AoU / Hillsborough survey variable -> plain-language meaning |
| `condition_concepts.csv` | OMOP condition concept ID -> disease / grouping |
| `lifestyle_variables.csv` | Lifestyle exposures (smoking, diet, activity, etc.) -> meaning |
| `phenotypes/` | One definition file per disease: the single source of truth |

## Why this matters

Both pipelines (AoU national cohort, Hazel Hillsborough cohort) build cases and controls from the
`phenotypes/` definitions via `src/hlp/phenotypes.py`. If a definition changes, it changes in one
place and both cohorts stay comparable. Never redefine a phenotype inside a notebook.

The CSV files are non-sensitive dictionaries and ARE committed (the root `.gitignore` re-allows
`codebook/`). Never put participant-level values in these files.
