# data/ (local only, never committed)

This directory holds participant-level data while you work. Nothing here is tracked by
git (see `.gitignore`). The structure below is a convention, not a commitment.

## What belongs here

| Path | Contents | Real source |
|------|----------|-------------|
| `data/survey/` | Hillsborough health + genealogy survey responses | Lab master package (see below); IRB #27626 |
| `data/genotype/` | Pointers / small derived files from saliva genotyping | Lives on NCSU Hazel; reference by path |

## Hillsborough survey data — source of record

The participant-level survey data and roster live OUTSIDE this repo, on the lab's FIPS-encrypted
drive under IRB #27626:

```
.../Hillsborough/Surveys/                         (raw Qualtrics exports, analysis, figures)
.../Hillsborough/Surveys/HLP_Master_Data_Package/ (roster, UUID master, completion matrix)
```

Only the **non-sensitive survey codebooks** (REDCap-style data dictionaries) were mirrored into
this repo, as `codebook/survey_variables.csv` and `codebook/lifestyle_variables.csv`. The raw
responses, participant roster, UUID master sheet, and any name/contact data are PII/PHI and stay
on the encrypted drive. To run the Hillsborough phenotyping locally, copy the cleaned response
CSV (keyed to the Adjusted UUIDs) into `data/survey/` here, where `.gitignore` keeps it untracked.
Note: the Health Survey instrument has no age/sex/race fields, so person-level covariates
(including the sex restriction for prostate/breast) require linkage to the UUID master sheet.

## Rules

1. **Never commit anything under `data/`.** The root and local `.gitignore` enforce this, but
   treat it as a manual rule too.
2. **Survey + genotype data stay local or on Hazel.** Do not upload this cohort's own data into
   the All of Us cloud workspace; the AoU Data Use Agreement prohibits importing external
   identifiable data.
3. The large genotype data lives on **Hazel**. Scripts reference Hazel paths rather than copying
   data down. Keep only small, non-identifiable derived summaries locally if needed.
