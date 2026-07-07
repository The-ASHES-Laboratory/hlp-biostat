"""Adapter for the compiled Hillsborough "combo summaries" sheet.

The working Hillsborough dataset is a grad-student compilation of the Qualtrics + paper surveys
(``data/HLP_Combo_summaries.xlsx``, gitignored, IRB #27626). Its schema is coarser than the
instrument codebook the generic classifiers target:

- Disease history is a per-condition ``per_<x>`` (personal) / ``fam_<x>`` (family) Yes/No split.
- **Cancer has no subtype** - only ``per_cancer`` (any cancer). Colorectal/prostate/breast cannot be
  separated, so the Hillsborough side collapses to a single ``any_cancer`` phenotype (underpowered,
  not comparable to the AoU per-subtype cancers).
- Lifestyle is **binary**, not the instrument's multi-select / ordinals (Smoking is only
  never/quit; Drinking, Exercise, Sleep are two-level).
- ``Sex`` / ``Age`` / ``Ethnicity`` are inline, so no UUID master-sheet linkage is needed here.
- Atrial fibrillation is dropped (only an any-CVD proxy, ``per_cardio``, exists).

This module maps that real schema to the canonical analysis frame, reusing ``survey_phenotypes``
(direct rules) for the three usable phenotypes and ``linkage.normalize_sex`` for sex. Pure mappers
are stdlib; ``load_combo_summaries`` / ``build_features`` import pandas lazily.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from hlp.linkage import normalize_sex
from hlp.survey_phenotypes import SurveyRule, build_survey_label_matrix

# data/ is gitignored; this path is where the working sheet lives locally.
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
COMBO_PATH = DATA_DIR / "HLP_Combo_summaries.xlsx"

# Three usable phenotypes as direct Yes/No rules over the per_<x> columns. AF omitted on purpose.
HILLSBOROUGH_RULES = {
    "hypertension": SurveyRule("hypertension", "direct", "per_hyper", frozenset({"yes"}), frozenset({"no"})),
    "asthma": SurveyRule("asthma", "direct", "per_resp", frozenset({"yes"}), frozenset({"no"})),
    "any_cancer": SurveyRule("any_cancer", "direct", "per_cancer", frozenset({"yes"}), frozenset({"no"})),
}


def _norm(value: object) -> str:
    """Strip + lowercase a cell; None/NaN/whitespace-junk (e.g. '\\n') -> ''."""
    if value is None or (isinstance(value, float) and value != value):
        return ""
    return str(value).strip().lower()


def _binary(value: object, ones: frozenset[str], zeros: frozenset[str]) -> Optional[int]:
    key = _norm(value)
    if key in ones:
        return 1
    if key in zeros:
        return 0
    return None


def ever_smoked(value: object) -> Optional[int]:
    """Smoking -> ever-smoked. This sheet only records never vs quit (no current smokers)."""
    return _binary(
        value,
        ones=frozenset({"quit smoking", "quit", "former", "smokes", "current"}),
        zeros=frozenset({"never used tobacco products", "never", "no tobacco"}),
    )


def drinks(value: object) -> Optional[int]:
    return _binary(value, frozenset({"drinks"}), frozenset({"never drinks"}))


def regular_exercise(value: object) -> Optional[int]:
    return _binary(value, frozenset({"regular physical activity"}), frozenset({"no regular physical activity"}))


def adequate_sleep(value: object) -> Optional[int]:
    """Above 6 hours -> 1, Below 6 hours -> 0."""
    return _binary(value, frozenset({"above 6 hours"}), frozenset({"below 6 hours"}))


def pollutant_exposure(value: object) -> Optional[int]:
    """Environmental pollutant exposure. Checklist item: 'Yes' = exposed; blank = none reported.

    (Documented assumption: the sheet has only 'Yes' / blank, so blank is treated as no exposure
    rather than missing. Flip to None here if blanks should be unknown.)
    """
    return 0 if _norm(value) in ("", "no", "none") else _binary(value, frozenset({"yes"}), frozenset())


def load_combo_summaries(path: Path = COMBO_PATH):
    """Load the combo-summaries sheet, tidy column names and string cells (pandas)."""
    import pandas as pd

    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"UUID": "participant_id"})
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].map(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def build_features(df, *, id_col: str = "participant_id"):
    """Map the tidied sheet to the canonical analysis frame indexed by participant.

    Columns: has_hypertension / has_asthma / has_any_cancer (1/0/<NA>), the lifestyle binaries
    (ever_smoked, drinks, regular_exercise, adequate_sleep, pollutant_exposure), and demographics
    (sex, age, ethnicity). Feeds ``risk`` and ``compare`` directly.
    """
    import pandas as pd

    def col(name):
        return df[name] if name in df.columns else pd.Series([None] * len(df))

    labels = build_survey_label_matrix(df, HILLSBOROUGH_RULES, id_col=id_col)

    idx = df[id_col].values
    feats = pd.DataFrame(index=idx)
    feats["ever_smoked"] = pd.array([ever_smoked(v) for v in col("Smoking")], dtype="Int64")
    feats["drinks"] = pd.array([drinks(v) for v in col("Drinking")], dtype="Int64")
    feats["regular_exercise"] = pd.array([regular_exercise(v) for v in col("Exercise")], dtype="Int64")
    feats["adequate_sleep"] = pd.array([adequate_sleep(v) for v in col("Sleep")], dtype="Int64")
    feats["pollutant_exposure"] = pd.array([pollutant_exposure(v) for v in col("Pollutants")], dtype="Int64")
    # Family history (fam_<x>) as Yes/No/None covariates, paralleling the three phenotypes.
    yes, no = frozenset({"yes"}), frozenset({"no"})
    feats["family_hypertension"] = pd.array([_binary(v, yes, no) for v in col("fam_hyper")], dtype="Int64")
    feats["family_asthma"] = pd.array([_binary(v, yes, no) for v in col("fam_resp")], dtype="Int64")
    feats["family_cancer"] = pd.array([_binary(v, yes, no) for v in col("fam_cancer")], dtype="Int64")

    feats["sex"] = [normalize_sex(v) for v in col("Sex")]
    feats["age"] = pd.to_numeric(col("Age"), errors="coerce").values
    feats["ethnicity"] = [(_norm(v).title() or None) for v in col("Ethnicity")]

    return labels.join(feats)
