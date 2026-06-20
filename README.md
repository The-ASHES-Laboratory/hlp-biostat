# hlp-biostat

Biostatistical / statistical-genetics component of the HLP project.

> This is one sub-component of the broader HLP project, not the whole thing. It covers the
> analysis arm: phenotyping, genetic association, and cohort comparison.

## Research question

How do genetic variants and lifestyle choices influence the risk of chronic conditions among
the African-American population in Hillsborough, NC, compared to the broader / national
African-American population?

**Phenotypes (6):** atrial fibrillation, prostate cancer, asthma, hypertension, colorectal
cancer, breast cancer.

## Cohorts

- **Hillsborough cohort:** 62 participants, saliva genotyping + health survey (the lab's own
  IRB-governed data).
- **National comparison cohort:** All of Us Research Program, controlled tier.

## Environments (one code source of truth)

| Environment | Role | Constraint |
|-------------|------|------------|
| This repo (local Mac) | Canonical source of truth for all code | Pushed to private GitHub |
| AoU Researcher Workbench | National AA cohort analysis | Controlled tier; data cannot be exported; clones this repo for code |
| NCSU Hazel (HPC) | Hillsborough cohort genomics | LSF now, Slurm later; data referenced by path, never committed |

## Layout

```
codebook/    Living data dictionary: survey vars, OMOP concepts, and the 6 phenotype definitions
src/hlp/     Shared, environment-agnostic analysis logic (imported by both aou/ and hpc/)
aou/         Entrypoints that run inside the AoU cloud workbench
hpc/         Entrypoints that run on Hazel
data/        Local-only, gitignored; never committed
analysis/    Cross-cohort reports (outputs stripped before commit)
manuscript/  Writing, figures, tables
docs/        Project docs, setup design, and the AoU 2.0 migration runbook
env/         Reproducible environments (conda + pip)
```

The 6 phenotypes are defined once in `codebook/phenotypes/`. Both the cloud and HPC entrypoints
build cases/controls from those same definitions via `src/hlp/phenotypes.py`, so the
Hillsborough-vs-national comparison stays apples-to-apples.

## Getting started

See `docs/setup-design.md` for the full design and `CONTRIBUTING.md` for the two rules that
keep this project safe. Roadmap and milestones live in `docs/ROADMAP.md`.
