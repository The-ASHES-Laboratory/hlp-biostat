# hlp-biostat: Repository Setup Design

*Date: 2026-06-20*

## Overview

`hlp-biostat` is the biostatistical / statistical-genetics component of the broader
HLP project. It is a deliberately scoped sub-component: it does not represent the whole
HLP project, only the analysis arm.

**Research question.** How do genetic variants and lifestyle choices influence the risk
of chronic conditions among the African-American population in Hillsborough, NC, compared
to the broader / national African-American population?

**Target phenotypes (6):** atrial fibrillation, prostate cancer, asthma, hypertension,
colorectal cancer, breast cancer.

**Cohorts.**
- **Hillsborough cohort:** 62 participants, saliva genotyping + health survey (the lab's
  own IRB-governed data).
- **National comparison cohort:** All of Us Research Program, controlled tier.

**People.** Carter Clinton (PI, reviewer/co-author). Jalen (undergraduate, works mostly
independently). Active over summer 2026 into the following academic year.

## Decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Repo role | Canonical monorepo: source of truth for all project code; cloud + HPC sync code FROM here |
| 2 | Hillsborough data location | Genotyping on HPC (NCSU Hazel); survey data local. Repo is code-only; data never committed |
| 3 | Collaboration model | Shared-branch: Carter and Jalen both commit to `main` directly; informal review |
| 4 | "Codebook" meaning | Co-equal deliverable: a living data dictionary AND the reproducible pipeline that consumes it |
| 5 | Repo name | `hlp-biostat` (clear sub-component of HLP, person-agnostic) |
| 6 | Planning machinery | Lightweight: this design spec + README + docs/ROADMAP.md; git history as progress log |

## Three runtime environments, one code source of truth

| Environment | Holds | Constraint |
|-------------|-------|------------|
| Local Mac (this repo) | All code, codebook, docs, manuscript | Canonical. Pushed to private GitHub |
| AoU Researcher Workbench (cloud) | National AA cohort analysis | Controlled tier. Data **cannot** be exported. Clones this repo for code |
| HPC Hazel | Hillsborough cohort genomics | LSF now, migrating to Slurm. Data referenced by path, never committed |

## Directory structure (Option C: hybrid)

```
hlp-biostat/
├── README.md                 # research question, environment map, how to run
├── CONTRIBUTING.md           # the two guardrail rules (see Governance)
├── .gitignore                # data/, secrets, notebook outputs, env cruft
│
├── codebook/                 # co-equal deliverable: the living data dictionary
│   ├── README.md
│   ├── survey_variables.csv      # AoU survey variable  -> plain meaning
│   ├── condition_concepts.csv    # OMOP condition concept ID -> disease
│   ├── lifestyle_variables.csv
│   └── phenotypes/               # 6 disease defs, one file each = single source of truth
│       ├── atrial_fibrillation.md
│       ├── prostate_cancer.md
│       ├── asthma.md
│       ├── hypertension.md
│       ├── colorectal_cancer.md
│       └── breast_cancer.md
│
├── src/hlp/                  # shared, environment-agnostic analysis logic (importable)
│   ├── __init__.py
│   ├── phenotypes.py             # builds case/control FROM codebook defs
│   ├── qc.py                     # PLINK 2.0 QC wrappers
│   ├── compare.py                # Hillsborough vs national comparison stats
│   └── plotting.py
│
├── aou/                      # entrypoints that RUN in the AoU cloud workbench
│   ├── README.md                 # controlled-tier rules: never commit outputs
│   └── (HLP_project.ipynb split/relocated here)
│
├── hpc/                      # entrypoints that RUN on Hazel
│   ├── README.md                 # LSF now, Slurm later
│   └── jobs/                      # submission scripts + QC / association steps
│
├── data/                    # GITIGNORED, local-only, never committed
│   ├── .gitignore                # ignore everything except README
│   └── README.md                 # what belongs here + real source + governance note
│
├── analysis/                # cross-cohort reports (outputs stripped before commit)
├── manuscript/              # writing, figures, tables
├── docs/                    # project docs, incl. AoU 2.0 migration runbook + this spec
└── env/                     # environment.yml (conda/Hazel) + requirements.txt (AoU pip)
```

Key properties:
- The 6 phenotypes are defined once in `codebook/phenotypes/`. Both `aou/` and `hpc/`
  entrypoints build cases/controls from these same files via `src/hlp/phenotypes.py`, so
  the Hillsborough-vs-national comparison stays apples-to-apples. This is the central
  reason for Option C over a per-environment split.
- The existing `HLP_project.ipynb` (cohort build + genomic pull) relocates into `aou/`.
- `data/` is present in the tree but empty in git; the local survey CSV lives there,
  gitignored, documented by its README.

## Data governance

The repo must never carry participant-level data or controlled-tier material. Two layers:

1. **Root `.gitignore`** ignores `data/` (all but its README) plus data extensions anywhere:
   `*.csv`, `*.tsv`, `*.vcf*`, `*.bed/.bim/.fam`, `*.pgen/.psam/.pvar`, `*.bgen`, `*.parquet`,
   plus secrets and env cruft. Codebook dictionaries are force-allowed back with negation
   rules (e.g. `!codebook/*.csv`).
2. **Notebook-output stripping** via a pre-commit hook (e.g. nbstripout) so no AoU notebook
   ever commits cell outputs.

`data/README.md` documents what belongs there and its real source (Hazel paths, local survey
origin) so the tree is self-describing without exposing anything.

**Hard rule:** the Hillsborough survey/genotype data stays local or on Hazel and is never
uploaded into the AoU cloud workspace (All of Us Data Use Agreement prohibits importing
external identifiable cohort data).

## Git and collaboration

- **Private GitHub repo.** Shared-branch model: both contributors commit to `main`; informal
  review.
- **`CONTRIBUTING.md`** codifies the two project-protecting rules:
  1. Never commit anything under `data/`.
  2. Phenotype changes happen only in `codebook/phenotypes/`, never inline in a notebook.
- The AoU cloud workspace clones this repo for code; results/outputs stay in the cloud.

## Execution checklist (setup)

1. Rename directory `JF_AoU_codebook` -> `hlp-biostat`.
2. Create directory skeleton + `.gitkeep`/README placeholders.
3. Write root `.gitignore`, `data/.gitignore`, and the governance READMEs.
4. Write `README.md`, `CONTRIBUTING.md`, `docs/ROADMAP.md`.
5. Relocate `HLP_project.ipynb` into `aou/`.
6. Add `env/environment.yml` + `env/requirements.txt` skeletons.
7. Add pre-commit notebook-output stripping config.
8. Commit; create private GitHub remote; push.

## Next task (separate phase)

**AoU Legacy Workbench -> Researcher Workbench 2.0 migration.** One-way, irreversible mirror.
Build a checklist runbook at `docs/migration-aou-2.0.md` from the official documentation
before executing, then run it carefully. Tracked as the first milestone in `docs/ROADMAP.md`.
