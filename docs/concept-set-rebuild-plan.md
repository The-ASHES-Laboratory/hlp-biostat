# Concept-Set Rebuild Plan (AoU Researcher Workbench 2.0)

*Created 2026-06-22. Do this in RW 2.0 after the migration completes.*

## STATUS: DONE 2026-07-07 (off-platform)
The AoU workspace CDR is unresolvable (superseded version; see `docs/migration-validation.md`), so
rather than wait, the rebuild was done against the **public OHDSI vocabulary** (ATLAS demo WebAPI),
which is the same OMOP vocabulary the CDR uses. Script: `analysis/rebuild_concept_sets.py`
(resolves each root's standard Condition descendants, keeps valid STANDARD concepts, rewrites
`codebook/condition_concepts.csv`). Reproducible; re-run any time.

Result (standard Condition concepts): asthma 116, hypertension 148, atrial_fibrillation 19,
colorectal_cancer 1896, prostate_cancer 178, breast_cancer 1907 (4,264 rows total). This removed the
two non-standard concepts (4108832, 4157332) and the contamination - each set is now purely the
descendants of its own root, so no cross-phenotype misfiling is possible.

**Decision (2026-07-07): cancer sets kept BROAD / faithful.** The roots "Malignant tumor of <organ>"
are site-based in SNOMED, so descendants include all malignancies at that organ (incl. rare
lymphoma/sarcoma-of-site concepts), which is why the cancer sets are large. This matches what AoU's
own "include descendants" builder produces; the rare post-coordinated concepts are ~never coded, so
practical impact is negligible. Can be tightened to carcinoma-only later if desired.

Rectum root resolved to concept 443390 ("Malignant tumor of rectum", SNOMED). ATLAS source key:
ATLASPROD. --- original plan below, for reference ---

## Why
The 2026-06-22 OHDSI Atlas audit found the notebook's original `CONDITION_CONCEPTS` was badly
contaminated: 11 of ~25 IDs were wrong (mostly asthma concepts misfiled under the cancers and AF).
The contaminated IDs were removed from `codebook/condition_concepts.csv`, which left the
cancer / AF / hypertension sets **thin** (prostate is down to a single concept). Rather than
hand-curate, rebuild each set properly with the **AoU Concept Set builder**, which expands a chosen
standard concept to all its descendants against the controlled-tier vocabulary.

## How (per phenotype, in the 2.0 Concept Set / Cohort builder)
1. Create a new Concept Set named `HLP_<phenotype>`.
2. Search for the **root standard concept** below, add it, and enable **"Include Descendants."**
3. Confirm the domain is **Condition** and the standard concept flag is **Standard**.
4. Export the full materialized concept list (all descendants) - that enumerated list is what we
   store; it makes the existing exact-match logic in `phenotypes.py` complete without needing
   runtime descendant expansion.

| Phenotype | Root standard concept to search/add | Verified concept_id | Notes |
|-----------|--------------------------------------|---------------------|-------|
| asthma | "Asthma" | 317009 | Current 4-concept set is already correct; rebuild only for descendant completeness |
| hypertension | "Hypertensive disorder" | 316866 | Descendants cover essential/secondary/etc. (drop bare "Essential hypertension" 320128 once rooted here) |
| atrial_fibrillation | "Atrial fibrillation" | 313217 | Descendants; this replaces the non-standard 4108832 |
| prostate_cancer | "Malignant tumor of prostate" | 4163261 | Descendants; restores the subtypes lost to contamination cleanup |
| breast_cancer | "Malignant tumor of breast" | 4112853 | Descendants; replaces the non-standard 4157332 |
| colorectal_cancer | "Malignant tumor of colon" + "Malignant tumor of rectum" | 4180790 (+ rectum) | Add colon AND rectum roots (search "colorectal"); current set has colon/hepatic-flexure/rectosigmoid only |

## After building (repo-side, back here)
1. Export each concept set's full concept-ID list from RW 2.0.
2. Replace the thin rows in `codebook/condition_concepts.csv` with the exported IDs (one row per
   concept, `disease_group` = phenotype, `include_descendants` = no since descendants are now
   enumerated). Fill `concept_name` from the export.
3. Re-run `python tests/test_phenotypes.py` (the integration test asserts each phenotype loads).
4. The AoU notebook reads concept sets from the codebook via hlp, so the corrected sets flow into
   the analysis automatically - no notebook edit needed.

## Validation
- After rebuild, no concept in any set should be non-standard (STANDARD_CONCEPT must be "S"); the
  builder enforces this. The two current non-standard concepts (4108832, 4157332) get resolved.
- Spot-check that no asthma/respiratory concept appears under a cancer or AF set (the original bug).
