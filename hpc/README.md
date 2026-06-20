# hpc/

Entrypoints that run on the **NCSU Hazel cluster** for the Hillsborough cohort.

## Notes
- Genotype data for the 62 participants lives on Hazel. Scripts reference cluster paths; data is
  never copied into this repo.
- Scheduler: **LSF now, migrating to Slurm**. Keep submission scripts in `jobs/` and parameterize
  the scheduler-specific bits so the Slurm move is a small diff.
- Use PLINK 2.0 (preferred over 1.9) for QC and association steps.
- Build cases/controls from `codebook/phenotypes/` via `src/hlp/`, same as the AoU side.

## Layout
- `jobs/` - submission scripts (LSF/Slurm) for QC, phenotyping, association.
