# Contributing to hlp-biostat

This is a shared-branch repo: contributors commit to `main` directly. Keep commits small and
descriptive so the history doubles as our progress log.

## Two rules that protect this project

1. **Never commit anything under `data/`.** No survey data, no genotype files, no participant-level
   anything. The `.gitignore` enforces it, but always sanity-check `git status` before committing.
2. **Phenotype definitions live only in `codebook/phenotypes/`.** Do not hard-code a disease
   definition inline in a notebook or script. Both the AoU (national) and Hazel (Hillsborough)
   pipelines must build cases/controls from the same definition files, or the cohort comparison
   is invalid.

## Working across environments

- **AoU Researcher Workbench (cloud):** clone this repo for code; controlled-tier data and all
  outputs stay in the cloud. Never download participant-level data or commit notebook cell outputs.
- **Hazel (HPC):** Hillsborough genotype data stays on the cluster; scripts reference cluster paths.
- **Local:** the survey CSV lives under `data/` (gitignored).

## Notebook hygiene

Notebook cell outputs can leak data and bloat diffs. Install the pre-commit hook so outputs are
stripped automatically:

```bash
pip install pre-commit nbstripout
pre-commit install
```

## Commit style

Plain, present-tense summaries (e.g. `add hypertension phenotype definition`). One logical change
per commit.
