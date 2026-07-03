"""Tests for src/hlp/hillsborough.py.

Adapter for the compiled Hillsborough "combo summaries" sheet (a grad-student compilation of
the Qualtrics + paper surveys). Its codings are coarser/binary and differ from the instrument
codebook, so this module maps the real columns to the canonical analysis frame, reusing the
survey_phenotypes direct rules and linkage.normalize_sex where clean.

Pure mappers run anywhere; build_features (pandas) skips without pandas. No real data here -
fixtures mimic the sheet's codings, including its junk values.

Run: python -m pytest tests/ -q   (or: python tests/test_hillsborough.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.hillsborough import (  # noqa: E402
    HILLSBOROUGH_RULES,
    adequate_sleep,
    drinks,
    ever_smoked,
    pollutant_exposure,
    regular_exercise,
)


# --- pure lifestyle mappers (this file's actual binary codings) -------------------------------
def test_ever_smoked():
    assert ever_smoked("Never used tobacco products") == 0
    assert ever_smoked("Quit smoking") == 1
    assert ever_smoked("") is None
    assert ever_smoked(None) is None


def test_drinks():
    assert drinks("Drinks") == 1
    assert drinks("Never drinks") == 0
    assert drinks("") is None


def test_regular_exercise():
    assert regular_exercise("Regular physical activity") == 1
    assert regular_exercise("No regular physical activity") == 0


def test_adequate_sleep():
    assert adequate_sleep("Above 6 hours") == 1
    assert adequate_sleep("Below 6 hours") == 0


def test_pollutant_exposure_blank_is_no_exposure():
    # exposure checklist: "Yes" = exposed; blank = none reported (documented assumption)
    assert pollutant_exposure("Yes") == 1
    assert pollutant_exposure("") == 0
    assert pollutant_exposure(None) == 0


def test_rules_cover_the_three_usable_phenotypes():
    assert set(HILLSBOROUGH_RULES) == {"hypertension", "asthma", "any_cancer"}
    assert HILLSBOROUGH_RULES["hypertension"].survey_item == "per_hyper"
    assert HILLSBOROUGH_RULES["asthma"].survey_item == "per_resp"
    assert HILLSBOROUGH_RULES["any_cancer"].survey_item == "per_cancer"
    # AF is intentionally absent (per_cardio is any-CVD, not ascertainable)
    assert "atrial_fibrillation" not in HILLSBOROUGH_RULES


# --- build_features (pandas) ------------------------------------------------------------------
def test_build_features_maps_the_sheet():
    try:
        import pandas as pd
    except ImportError:
        print("SKIP test_build_features_maps_the_sheet (pandas not installed)")
        return

    from hlp.hillsborough import build_features

    df = pd.DataFrame(
        [
            {"participant_id": "u1", "per_hyper": "Yes", "per_resp": "No", "per_cancer": "No",
             "Smoking": "Quit smoking", "Drinking": "Drinks", "Exercise": "Regular physical activity",
             "Sleep": "Above 6 hours", "Pollutants": "Yes", "Sex": "M", "Age": 60,
             "Ethnicity": "African American"},
            {"participant_id": "u2", "per_hyper": "No", "per_resp": "Yes", "per_cancer": "Yes",
             "Smoking": "Never used tobacco products", "Drinking": "Never drinks",
             "Exercise": "No regular physical activity", "Sleep": "Below 6 hours", "Pollutants": None,
             "Sex": "F", "Age": 45, "Ethnicity": "Mixed ancestry"},
            {"participant_id": "u3", "per_hyper": "Unsure", "per_resp": "No", "per_cancer": "\n",
             "Smoking": None, "Drinking": None, "Exercise": None, "Sleep": None, "Pollutants": None,
             "Sex": "F", "Age": 70, "Ethnicity": "African American"},
        ]
    )
    f = build_features(df)

    def get(pid, col):
        v = f.loc[pid, col]
        return None if pd.isna(v) else v

    # phenotype labels (direct Yes/No; Unsure/junk -> missing)
    assert get("u1", "has_hypertension") == 1
    assert get("u1", "has_asthma") == 0
    assert get("u2", "has_asthma") == 1
    assert get("u2", "has_any_cancer") == 1
    assert get("u3", "has_hypertension") is None      # "Unsure" -> missing
    assert get("u3", "has_any_cancer") is None        # junk "\n" -> missing
    assert "has_atrial_fibrillation" not in f.columns  # AF dropped

    # lifestyle binaries
    assert get("u1", "ever_smoked") == 1 and get("u2", "ever_smoked") == 0
    assert get("u1", "drinks") == 1 and get("u2", "drinks") == 0
    assert get("u1", "adequate_sleep") == 1 and get("u2", "adequate_sleep") == 0
    assert get("u1", "pollutant_exposure") == 1 and get("u2", "pollutant_exposure") == 0

    # demographics (sex inline -> no master-sheet linkage needed)
    assert get("u1", "sex") == "male" and get("u2", "sex") == "female"
    assert get("u1", "age") == 60


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
