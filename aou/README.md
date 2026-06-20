# aou/

Entrypoints that run **inside the All of Us Researcher Workbench** (cloud Jupyter).

## Controlled-tier rules
- Data lives in the cloud and **cannot be exported**. Never download participant-level data.
- **Never commit notebook cell outputs.** The pre-commit hook (nbstripout) strips them; keep it
  installed. Outputs can contain participant data or sub-threshold counts.
- Import shared logic from `src/hlp/` (clone this repo into the workbench). Build cases/controls
  from `codebook/phenotypes/`, never from inline definitions.

## Contents
- `HLP_project.ipynb` - existing cohort build + survey/condition merge + genomic data access
  (exome / microarray PLINK from `gs://fc-aou-datasets-controlled`). To be split into focused
  notebooks (cohort build, phenotype extract, genomic pull) over time.
