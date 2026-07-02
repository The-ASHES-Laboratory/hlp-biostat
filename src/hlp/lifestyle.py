"""Derive analysis-ready lifestyle covariates from the Hillsborough Health Survey.

Turns the raw survey items in ``codebook/lifestyle_variables.csv`` into the modifiable-risk-factor
covariates the association / risk models need (smoking, alcohol, physical activity, sleep). The
survey records these as a mix of a multi-select checkbox (smoking), plain ordinals (alcohol, sleep),
and a gated branch (exercise Yes/No -> days per week), so each needs its own small derivation.

Contract mirrors the rest of ``hlp``: pure-Python core returning canonical values or ``None`` for
"missing / prefer-not-to-answer", plus a lazy-pandas ``derive_lifestyle_features`` wrapper that
emits one feature frame indexed by participant.

Derivations:
- ``smoking_status``  -> "never" / "former" / "current" / None, collapsing the multi-select with
  precedence current > former > never. NOTE (domain call, easy to change below): ChewingTobacco is
  counted as *current tobacco use*. For a strictly-smoking covariate, drop it from
  ``_SMOKING_CURRENT``.
- ``alcohol_level``   -> ordinal 0..4 (never..daily).
- ``sleep_level``     -> ordinal 0..3 (<4h .. >8h).
- ``exercise_level``  -> gated ordinal: 0 (does not exercise) / 1..3 by days-per-week; None if the
  gate is unknown or the participant exercises but the frequency is missing.

Diet and environment items are intentionally deferred (microbiome-focused; add here when needed).
"""

from __future__ import annotations

import re
from typing import Optional

# Smoking multi-select tokens (normalized). ChewingTobacco -> current tobacco use (see module note).
_SMOKING_CURRENT = frozenset({"cigarettes", "othersmokingtobacco", "chewingtobacco"})
_SMOKING_FORMER = frozenset({"quit"})
_SMOKING_NEVER = frozenset({"notobacco"})

# Ordinal scales (index = code).
_ALCOHOL_ORDER = ("never", "rarely", "occasionally", "regularly", "daily")
_SLEEP_ORDER = ("less4", "4to6", "6to8", "more8")
_EXERCISE_DAYS = {"1to2days": 1, "3to4days": 2, "5to7days": 3}

_MULTI_DELIM = re.compile(r"[|,;/]")


def _norm(value: object) -> str:
    """Strip + lowercase a scalar response; None/NaN/blank -> ''."""
    if value is None or (isinstance(value, float) and value != value):  # NaN
        return ""
    return str(value).strip().lower()


def _split_multi(value: object) -> set[str]:
    """Parse a multi-select response (delimited string or iterable) into normalized tokens."""
    if value is None or (isinstance(value, float) and value != value):
        return set()
    if isinstance(value, str):
        parts: object = _MULTI_DELIM.split(value)
    else:
        try:
            parts = list(value)
        except TypeError:
            return set()
    return {t for t in (_norm(p) for p in parts) if t}


def smoking_status(forms: object) -> Optional[str]:
    """Collapse the multi-select tobacco form to never/former/current (precedence in that order)."""
    tokens = _split_multi(forms)
    if tokens & _SMOKING_CURRENT:
        return "current"
    if tokens & _SMOKING_FORMER:
        return "former"
    if tokens & _SMOKING_NEVER:
        return "never"
    return None


def alcohol_level(value: object) -> Optional[int]:
    """Alcohol frequency as an ordinal 0 (never) .. 4 (daily); None if missing/PNA."""
    key = _norm(value)
    return _ALCOHOL_ORDER.index(key) if key in _ALCOHOL_ORDER else None


def sleep_level(value: object) -> Optional[int]:
    """Sleep hours/night as an ordinal 0 (<4h) .. 3 (>8h); None if missing/PNA."""
    key = _norm(value)
    return _SLEEP_ORDER.index(key) if key in _SLEEP_ORDER else None


def exercise_level(exercises: object, days: object) -> Optional[int]:
    """Gated exercise ordinal: 0 if does not exercise; 1..3 by days/week; None if unknown."""
    gate = _norm(exercises)
    if gate == "no":
        return 0
    if gate == "yes":
        return _EXERCISE_DAYS.get(_norm(days))  # None if frequency missing/unknown
    return None  # gate unknown / PNA


def derive_lifestyle_features(
    survey_df,
    *,
    id_col: str = "participant_id",
    smoking_col: str = "smoking_tobaccoform",
    alcohol_col: str = "alcohol_drinkingfrequency",
    exercise_gate_col: str = "physicalactivity_exercisefrequency",
    exercise_days_col: str = "exercisefrequency_daysperweek",
    sleep_col: str = "sleep_hourspernight",
):
    """Derive the lifestyle covariate frame from the survey (pandas wrapper).

    Returns a DataFrame indexed by participant id with: ``smoking_status`` (str/None), the
    ``ever_smoked`` / ``current_smoker`` binaries, and the ``alcohol_level`` / ``exercise_level`` /
    ``sleep_level`` ordinals (all nullable ``Int64``). Missing columns are tolerated (treated as
    unanswered).
    """
    import pandas as pd

    def derive_row(row):
        status = smoking_status(row.get(smoking_col))
        return pd.Series(
            {
                "smoking_status": status,
                "ever_smoked": None if status is None else int(status in ("current", "former")),
                "current_smoker": None if status is None else int(status == "current"),
                "alcohol_level": alcohol_level(row.get(alcohol_col)),
                "exercise_level": exercise_level(row.get(exercise_gate_col), row.get(exercise_days_col)),
                "sleep_level": sleep_level(row.get(sleep_col)),
            }
        )

    out = survey_df.apply(derive_row, axis=1)
    out.index = survey_df[id_col].values
    for col in ("ever_smoked", "current_smoker", "alcohol_level", "exercise_level", "sleep_level"):
        out[col] = out[col].astype("Int64")
    return out
