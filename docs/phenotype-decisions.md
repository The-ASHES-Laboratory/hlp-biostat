# Phenotype Definitions: What Changed and Why

*Collaborator-facing summary for Jalen Franklin. Covers the phenotype work since the original
`HLP_project.ipynb`: the concept-set QC, the move to a codebook single-source-of-truth, the case
rules, and the new Hillsborough survey side. Prepared 2026-07-02.*

The 6 phenotypes: asthma, hypertension, atrial fibrillation, colorectal / prostate / breast cancer.

## 1. Definitions moved out of the notebook into the codebook
The definitions now live in `codebook/` as the single source of truth, not as inline lists in the
notebook:
- `condition_concepts.csv` - the OMOP concept set per phenotype
- `phenotype_params.csv` - the case rule (occurrence threshold, sex restriction)
- `phenotypes/<name>.md` - the human-readable rationale
- `survey_rules.csv` - the Hillsborough survey rule per phenotype (see section 4)

**Why:** both pipelines (the AoU national cohort and the Hazel Hillsborough cohort) read the same
definitions via the shared `hlp` package. A definition change propagates to both at once, which is
what keeps the two-cohort comparison apples-to-apples. The notebook consumes the codebook instead
of hard-coding `concept_id IN (...)` lists, so it does not need to be re-authored.

## 2. Concept sets were QC'd against OHDSI Atlas - 11 contaminated IDs removed
This is the most important adjustment. An Atlas audit of the ~25 original concept IDs found **11
were wrong**, almost all of them **asthma / respiratory concepts misfiled under the cancer and AF
sets**. Examples:
- "Mild asthma", "Moderate asthma", "Chemical-induced asthma" were under **breast cancer**
- "Cough variant asthma", "IgE-mediated allergic asthma" were under **atrial fibrillation**
- "Late onset asthma" was under **prostate cancer**; "Wheezing" under **hypertension**
- "Carcinoma in situ of prostate" was under **colorectal cancer**

**Why it mattered:** left in place, these would have generated false-positive cases (e.g. an asthma
patient miscounted as a breast-cancer case), which would bias every downstream association. Asthma
was the only set that was already clean. All 11 were removed and the sets re-verified in Atlas.
Per-phenotype removal notes are in each `codebook/phenotypes/<name>.md` under "2026-06-22 QC".

**Consequence (known, tracked):** removing the contamination left the cancer / AF / hypertension
sets **thin** (prostate is down to a single parent concept). That is expected. The fix is a proper
rebuild in the AoU 2.0 Concept Set builder (root concept + "include descendants"), planned in
`docs/concept-set-rebuild-plan.md`. We chose to rebuild from standard roots rather than hand-curate.

## 3. Case rules were formalized
- **Rule-of-two** for chronic conditions (asthma, hypertension, AF): a case needs >=2 condition
  codes on **distinct days**, to cut EHR single-mention false positives.
- **>=1** for the cancers: a single diagnosis code is reliable.
- **Sex restriction:** prostate = male only, breast = female only, applied to **both** cases and
  controls.
- Exact concept matching for now (descendant expansion is a forward hook, pending the 2.0 rebuild).

## 4. New: the Hillsborough survey side is now implemented
The same 6 definitions now have a survey-based classifier (`src/hlp/survey_phenotypes.py`) so the
local cohort is phenotyped consistently with AoU. It emits the same case/control output as the AoU
side (1 case, 0 control, missing = excluded), so both cohorts feed the comparison identically.
Mapping and honest caveats:

| Phenotype | Hillsborough survey rule | Ascertainment note |
|-----------|--------------------------|--------------------|
| hypertension | `diagnosed_highbloodpressure` Yes/No | Cleanest match of the six |
| asthma | `diagnosed_respiratoryissues` Yes/No | **Over-broad**: item asks "asthma OR other respiratory", so over-ascertains vs the AoU asthma-specific set |
| atrial fibrillation | none | **Not ascertainable** (no AF item; closest is any-CVD). Dropped from the cross-cohort comparison by default rather than compare a misleading proxy |
| colorectal / prostate / breast | `diagnosed_cancer` = Yes + free-text `cancer_specify` parsed for type | Someone with a *different* cancer is excluded from controls, not counted as healthy. Prostate male-only, breast female-only (sex from UUID linkage to the master sheet, since the survey has no sex field) |

The cancer keyword lists that drive the `cancer_specify` parse live in `codebook/survey_rules.csv`
and are seeded defaults, easy to tune without code changes.

**Overall caveat for the comparison:** AoU ascertains from EHR condition codes; Hillsborough from
survey self-report. Different mechanisms, so the two-cohort contrast should be read with that in
mind, especially for asthma (over-broad) and AF (dropped).

## 5. Minor: one stale test datum fixed
A unit test still referenced concept `200970`, one of the IDs removed in the QC above, as a
colorectal case. Restored it to a valid colorectal concept (`4180790`). No effect on the
definitions, just test hygiene.

## Net effect on the notebook
Nothing to redo. It reads the corrected definitions from the codebook. The one open dependency is
the concept-set rebuild in AoU 2.0, which restores the thin cancer / AF / hypertension sets to full
descendant coverage. See `docs/concept-set-rebuild-plan.md`.
