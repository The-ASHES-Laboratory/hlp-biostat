"""Tests for src/hlp/lifestyle.py.

Derive analysis-ready lifestyle covariates from the Hillsborough Health Survey items
(codebook/lifestyle_variables.csv): smoking status from the multi-select, ordinal alcohol /
sleep, and gated exercise level. Pure-Python core; the pandas wrapper skips without pandas.

Run: python -m pytest tests/ -q   (or: python tests/test_lifestyle.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.lifestyle import (  # noqa: E402
    alcohol_level,
    exercise_level,
    sleep_level,
    smoking_status,
)


# --- smoking: collapse the multi-select tobacco form to never/former/current -----------------
def test_smoking_never_former_current():
    assert smoking_status({"NoTobacco"}) == "never"
    assert smoking_status({"Quit"}) == "former"
    assert smoking_status({"Cigarettes"}) == "current"
    assert smoking_status({"OtherSmokingTobacco"}) == "current"
    assert smoking_status({"ChewingTobacco"}) == "current"  # current tobacco use (smokeless)


def test_smoking_precedence_current_over_former_over_never():
    # any current use wins; then former (Quit) beats never (NoTobacco)
    assert smoking_status({"Cigarettes", "Quit"}) == "current"
    assert smoking_status({"Quit", "NoTobacco"}) == "former"


def test_smoking_accepts_delimited_string():
    assert smoking_status("Cigarettes | Quit") == "current"
    assert smoking_status("NoTobacco") == "never"


def test_smoking_missing_is_none():
    assert smoking_status({"Prefer not to answer"}) is None
    assert smoking_status(set()) is None
    assert smoking_status("") is None
    assert smoking_status(None) is None


# --- alcohol: ordinal 0..4 -------------------------------------------------------------------
def test_alcohol_ordinal():
    assert alcohol_level("Never") == 0
    assert alcohol_level("Rarely") == 1
    assert alcohol_level("Occasionally") == 2
    assert alcohol_level("Regularly") == 3
    assert alcohol_level("Daily") == 4
    assert alcohol_level("Prefer not to answer") is None
    assert alcohol_level("") is None


# --- sleep: ordinal 0..3 ---------------------------------------------------------------------
def test_sleep_ordinal():
    assert sleep_level("Less4") == 0
    assert sleep_level("4to6") == 1
    assert sleep_level("6to8") == 2
    assert sleep_level("More8") == 3
    assert sleep_level("Prefer not to answer") is None


# --- exercise: gated ordinal (No -> 0; Yes -> 1..3 by days/week) ------------------------------
def test_exercise_gated_ordinal():
    assert exercise_level("No", None) == 0            # doesn't exercise -> lowest, days irrelevant
    assert exercise_level("Yes", "1to2Days") == 1
    assert exercise_level("Yes", "3to4Days") == 2
    assert exercise_level("Yes", "5to7Days") == 3


def test_exercise_unknown_is_none():
    assert exercise_level("Prefer not to answer", None) is None  # gate unknown
    assert exercise_level("Yes", None) is None                   # exercises but frequency missing
    assert exercise_level("", "") is None


# --- pandas wrapper --------------------------------------------------------------------------
def test_derive_lifestyle_features_wrapper():
    try:
        import pandas as pd
    except ImportError:
        print("SKIP test_derive_lifestyle_features_wrapper (pandas not installed)")
        return

    from hlp.lifestyle import derive_lifestyle_features

    survey = pd.DataFrame(
        [
            {"participant_id": "u1", "smoking_tobaccoform": "Cigarettes",
             "alcohol_drinkingfrequency": "Daily", "physicalactivity_exercisefrequency": "No",
             "exercisefrequency_daysperweek": "", "sleep_hourspernight": "Less4"},
            {"participant_id": "u2", "smoking_tobaccoform": "NoTobacco",
             "alcohol_drinkingfrequency": "Never", "physicalactivity_exercisefrequency": "Yes",
             "exercisefrequency_daysperweek": "5to7Days", "sleep_hourspernight": "6to8"},
            {"participant_id": "u3", "smoking_tobaccoform": "Quit",
             "alcohol_drinkingfrequency": "Prefer not to answer",
             "physicalactivity_exercisefrequency": "Yes",
             "exercisefrequency_daysperweek": "", "sleep_hourspernight": "Prefer not to answer"},
        ]
    )
    f = derive_lifestyle_features(survey)

    def get(pid, col):
        v = f.loc[pid, col]
        return None if pd.isna(v) else v

    assert get("u1", "smoking_status") == "current"
    assert get("u1", "current_smoker") == 1
    assert get("u1", "ever_smoked") == 1
    assert get("u1", "alcohol_level") == 4
    assert get("u1", "exercise_level") == 0
    assert get("u1", "sleep_level") == 0

    assert get("u2", "smoking_status") == "never"
    assert get("u2", "ever_smoked") == 0
    assert get("u2", "exercise_level") == 3

    assert get("u3", "smoking_status") == "former"
    assert get("u3", "ever_smoked") == 1
    assert get("u3", "current_smoker") == 0
    assert get("u3", "alcohol_level") is None    # PNA -> missing
    assert get("u3", "exercise_level") is None   # exercises but days missing


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            print(f"FAIL {fn.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
