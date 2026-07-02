"""Build case/control labels from the Hillsborough Health Survey.

Companion to ``phenotypes.py`` (the AoU/OMOP side). Same output contract so both cohorts
feed ``compare.py`` identically:

    1    -> case
    0    -> control
    None -> excluded / missing (sex-restricted out, "Unsure"/"Prefer not to answer", or
            has a DIFFERENT cancer than the one being scored)

The survey rules are the single source of truth in ``codebook/survey_rules.csv`` and mirror the
``## Case definition`` blocks in ``codebook/phenotypes/<name>.md``. Three rule types:

- ``direct``            : one Yes/No item maps straight to case/control (hypertension, asthma).
- ``cancer_freetext``   : a gateway item (``diagnosed_cancer``) plus free-text ``cancer_specify``
                          parsed for the specific cancer. Gateway Yes + keyword match -> case;
                          gateway No -> control; gateway Yes but a different cancer -> excluded
                          from controls (None), so a colorectal control is never someone who
                          actually has breast cancer.
- ``not_ascertainable`` : the survey cannot capture this phenotype (atrial fibrillation has no
                          AF-specific item); every participant is None and the phenotype is
                          dropped from the Hillsborough matrix by default.

Sex for the sex-restricted cancers is NOT in the survey; it comes from UUID linkage to the master
sheet and is passed in explicitly (``sex="male"|"female"``), matching the AoU sex restriction.

The core (``classify_person_survey``, ``load_survey_rules``) is pure-Python / stdlib-only, so it is
testable anywhere. ``build_survey_labels`` / ``build_survey_label_matrix`` are thin pandas wrappers
(pandas imported lazily).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping, Optional

# Repo layout: src/hlp/survey_phenotypes.py -> parents[2] is the repo root.
CODEBOOK_DIR = Path(__file__).resolve().parents[2] / "codebook"
SURVEY_RULES_CSV = CODEBOOK_DIR / "survey_rules.csv"

RULE_TYPES = ("direct", "cancer_freetext", "not_ascertainable")
SPECIFY_ITEM = "cancer_specify"


def _norm(value: object) -> str:
    """Canonicalize a survey response: strip + lowercase; None/blank -> ''."""
    return "" if value is None else str(value).strip().lower()


def _split_norm(value: object) -> frozenset[str]:
    """Parse a pipe-separated codebook cell into a set of normalized tokens."""
    return frozenset(t for t in (_norm(v) for v in str(value or "").split("|")) if t)


@dataclass(frozen=True)
class SurveyRule:
    """One phenotype's Hillsborough survey case/control rule, from ``survey_rules.csv``."""

    name: str
    rule_type: str
    survey_item: Optional[str] = None
    case_values: frozenset[str] = field(default_factory=frozenset)
    control_values: frozenset[str] = field(default_factory=frozenset)
    cancer_keywords: frozenset[str] = field(default_factory=frozenset)
    sex_restriction: Optional[str] = None  # None | "male" | "female"
    specify_item: str = SPECIFY_ITEM

    def __post_init__(self) -> None:
        if self.rule_type not in RULE_TYPES:
            raise ValueError(f"{self.name}: rule_type must be one of {RULE_TYPES}, got {self.rule_type!r}")
        if self.sex_restriction not in (None, "male", "female"):
            raise ValueError(
                f"{self.name}: sex_restriction must be None/'male'/'female', got {self.sex_restriction!r}"
            )
        if self.rule_type in ("direct", "cancer_freetext"):
            if not self.survey_item:
                raise ValueError(f"{self.name}: {self.rule_type} rule needs a survey_item")
            if not (self.case_values and self.control_values):
                raise ValueError(f"{self.name}: {self.rule_type} rule needs case_values and control_values")
        if self.rule_type == "cancer_freetext" and not self.cancer_keywords:
            raise ValueError(f"{self.name}: cancer_freetext rule needs cancer_keywords")


def _matches_cancer(specify_text: str, keywords: frozenset[str]) -> bool:
    """Does the free-text cancer description name this phenotype's cancer?

    Case-insensitive substring match against the phenotype's keyword list (already normalized).
    Substring (not word-boundary) so "colon cancer", "colorectal", "rectal tumor" all match. The
    keyword lists live in ``survey_rules.csv`` and are the domain-owned knob for this parse.
    """
    return any(k in specify_text for k in keywords)


def classify_person_survey(
    responses: Mapping[str, object],
    rule: SurveyRule,
    *,
    sex: Optional[str] = None,
) -> Optional[int]:
    """Classify one participant for one phenotype from their survey responses.

    Parameters
    ----------
    responses : mapping of survey variable_id -> response (includes ``cancer_specify`` for cancers).
    rule      : the SurveyRule.
    sex       : "male"/"female"/None, from UUID linkage to the master sheet. Only used by
                sex-restricted phenotypes; a restricted phenotype excludes the wrong/unknown sex.

    Returns 1 (case), 0 (control), or None (excluded / missing).
    """
    if rule.rule_type == "not_ascertainable":
        return None

    # Sex restriction first, matching the AoU side: wrong or unknown sex -> excluded from both arms.
    if rule.sex_restriction is not None and sex != rule.sex_restriction:
        return None

    answer = _norm(responses.get(rule.survey_item))

    if rule.rule_type == "direct":
        if answer in rule.case_values:
            return 1
        if answer in rule.control_values:
            return 0
        return None  # Unsure / Prefer not to answer / missing

    # cancer_freetext: gateway item + free-text specify
    if answer in rule.control_values:
        return 0  # diagnosed_cancer == No -> eligible control
    if answer in rule.case_values:
        specify = _norm(responses.get(rule.specify_item))
        if _matches_cancer(specify, rule.cancer_keywords):
            return 1  # has this cancer -> case
        return None  # has a cancer, but not this one (or unspecified) -> excluded from controls
    return None  # gateway Unsure / Prefer not to answer / missing


def load_survey_rules(path: Path = SURVEY_RULES_CSV) -> dict[str, SurveyRule]:
    """Assemble every survey rule from ``codebook/survey_rules.csv``."""
    rules: dict[str, SurveyRule] = {}
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("phenotype") or "").strip()
            if not name:
                continue
            rules[name] = SurveyRule(
                name=name,
                rule_type=(row.get("rule_type") or "").strip(),
                survey_item=((row.get("survey_item") or "").strip() or None),
                case_values=_split_norm(row.get("case_values")),
                control_values=_split_norm(row.get("control_values")),
                cancer_keywords=_split_norm(row.get("cancer_keywords")),
                sex_restriction=((row.get("sex_restriction") or "").strip() or None),
            )
    return rules


def build_survey_labels(
    survey_df,
    rule: SurveyRule,
    *,
    id_col: str = "participant_id",
    sex_col: str = "sex",
):
    """Build a case/control label Series for one phenotype over the survey cohort (pandas wrapper).

    ``survey_df`` is one row per participant, columns = survey variable_ids (plus ``cancer_specify``
    and a ``sex`` column resolved from the master-sheet linkage). Returns an ``Int64`` Series indexed
    by participant id: 1 case, 0 control, <NA> excluded/missing.
    """
    import pandas as pd

    def label_row(row) -> Optional[int]:
        responses = row.to_dict()
        sex = responses.get(sex_col)
        sex = None if sex is None or (isinstance(sex, float) and pd.isna(sex)) else _norm(sex)
        return classify_person_survey(responses, rule, sex=sex or None)

    values = survey_df.apply(label_row, axis=1)
    series = pd.Series(values.values, index=survey_df[id_col].values, name=f"has_{rule.name}")
    return series.astype("Int64")


def build_survey_label_matrix(
    survey_df,
    rules: Optional[dict[str, SurveyRule]] = None,
    *,
    drop_not_ascertainable: bool = True,
    **kwargs,
):
    """Build a participant_id x has_<phenotype> matrix from the survey (pandas wrapper).

    Column names match the AoU-side ``build_label_matrix`` (``has_asthma``, ...), so the two cohorts
    line up for ``compare.py``. Phenotypes the survey cannot ascertain (atrial fibrillation) are
    dropped by default; pass ``drop_not_ascertainable=False`` to include them as an all-<NA> column.
    """
    import pandas as pd

    if rules is None:
        rules = load_survey_rules()
    columns = {
        f"has_{name}": build_survey_labels(survey_df, rule, **kwargs)
        for name, rule in rules.items()
        if not (drop_not_ascertainable and rule.rule_type == "not_ascertainable")
    }
    return pd.DataFrame(columns)
