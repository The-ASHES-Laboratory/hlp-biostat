# AoU Notebook Reconciliation

*2026-07-07. Our Jun-20 refactor (`aou/HLP_project.ipynb`) vs Jalen's Jun-21 cloud notebook
(`aou/HLP_project.cloud-jun21.ipynb`, pulled from the workspace bucket, outputs cleared).*

## Method
Whitespace-normalized cell-by-cell diff (the raw diff is ~1,100 lines of trailing-whitespace noise;
after normalizing, 19 of ~27 code cells are identical). Cells matched by their `CELL N` / `CELL PN`
labels.

## Key finding
**Jalen's cloud CELL 2 still hardcodes the pre-QC contaminated concept sets** - the exact IDs the
2026-06-22 audit removed (colorectal `200970/252658/252946`, breast `4155468/4155469/4157332/4245676`,
AF `313236/312950`). Our refactor loads the cleaned sets from the codebook instead. So our version is
canonical for the concept/case-definition cells; adopting Jalen's would re-introduce the contamination.
Jalen did make two genuine downstream improvements worth keeping.

## Decisions (per differing cell)
| Cell | Keep | Why |
|------|------|-----|
| Setup | OURS, minus one block | Delete the bogus `os.environ["WORKSPACE_CDR"]="your_cdr_project_id"` "Colab" placeholder we had added; it is wrong for AoU. |
| CELL 2 (concepts) | **OURS** | Loads cleaned sets from codebook via hlp. Jalen's inline lists are pre-QC contaminated. |
| CELL 5 (flags) | **OURS** | Delegates to `hlp.build_label_matrix` (rule-of-two + sex restriction). Jalen's is a naive `isin` (any occurrence = case, no thresholds). |
| CELL 6 | OURS | Matches our CELL 5 signature. |
| CELL P3 | **ADOPT JALEN** | Real bugfix: ours references an undefined `merged_df`; his uses the loaded `phenotype_df`. |
| CELL P4 (genomic) | **ADOPT JALEN** | His "Locate and Copy AoU Genomic Data" adds the actual `gsutil` copy step (v8 microarray/exome). More complete than our "find path". |
| CELL P5 (PLINK) | ADOPT JALEN | Template referencing his `LOCAL_GENO_DIR`. |
| trailing whitespace | ignore | cosmetic |

`new5.cloud.ipynb` = an nbformat output-stripping utility, not analysis. Ignore/delete.

## Pending (do in one pass once AoU re-points the workspace to cdrv9 / C2025Q4R6)
Execute the merge above into `aou/HLP_project.ipynb` AND update all CDR/genomic paths from the retired
v8 (`fc-aou-datasets-controlled/v8/...`, `C2024Q3R9`) to the current CDR. Deferred because it needs a
working environment to test and the paths change with the re-point anyway. Jalen's version is
committed as the reference so nothing is lost in the meantime.
