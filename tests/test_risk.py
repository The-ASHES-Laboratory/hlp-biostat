"""Tests for src/hlp/risk.py.

Logistic risk models (phenotype ~ lifestyle + demographics) via statsmodels. The formula
builder is pure/stdlib; the model-fitting tests need pandas + statsmodels and skip cleanly
when they are absent (matching the compare.py / wrapper convention).

Run: python -m pytest tests/ -q   (or: python tests/test_risk.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.risk import build_formula, fit_risk_model  # noqa: E402


# --- pure: formula builder -------------------------------------------------------------------
def test_build_formula_basic():
    assert build_formula("has_hypertension", ["alcohol_level", "sleep_level"]) == (
        "has_hypertension ~ alcohol_level + sleep_level"
    )


def test_build_formula_wraps_categoricals():
    f = build_formula("has_hypertension", ["smoking_status", "alcohol_level"], categorical={"smoking_status"})
    assert f == "has_hypertension ~ C(smoking_status) + alcohol_level"


def test_build_formula_requires_a_predictor():
    try:
        build_formula("y", [])
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for no predictors")


# --- helpers for synthetic, deterministic cohorts --------------------------------------------
PER_LEVEL = 10  # participants per covariate level


def _rows_for_level(level_col, level, n_case):
    # n_case out of PER_LEVEL are cases; the rest controls. Kept in [0.2, 0.8] so the logistic fit
    # is well-identified (no perfect separation / fitted probabilities pinned at 0 or 1).
    return (
        [{level_col: level, "has_htn": 1} for _ in range(n_case)]
        + [{level_col: level, "has_htn": 0} for _ in range(PER_LEVEL - n_case)]
    )


def _skip_if_no_deps(name):
    try:
        import pandas  # noqa: F401
        import statsmodels  # noqa: F401
        return False
    except ImportError:
        print(f"SKIP {name} (pandas/statsmodels not installed)")
        return True


# --- model fitting ---------------------------------------------------------------------------
def test_risk_factor_has_or_above_one_and_metadata():
    if _skip_if_no_deps("test_risk_factor_has_or_above_one_and_metadata"):
        return
    import pandas as pd

    # monotonic increasing case rate with alcohol level -> positive association, well-identified
    rows = []
    for level, n_case in [(0, 2), (1, 3), (2, 5), (3, 7), (4, 8)]:
        rows += _rows_for_level("alcohol_level", level, n_case)
    df = pd.DataFrame(rows)

    rm = fit_risk_model(df, "has_htn", ["alcohol_level"])

    assert rm.n == 50
    assert rm.n_cases == 25 and rm.n_controls == 25
    assert rm.converged
    row = rm.terms.set_index("term").loc["alcohol_level"]
    assert row["odds_ratio"] > 1.0                       # risk factor
    assert row["ci_low"] < row["odds_ratio"] < row["ci_high"]
    assert 0.0 <= row["p_value"] <= 1.0


def test_protective_factor_has_or_below_one():
    if _skip_if_no_deps("test_protective_factor_has_or_below_one"):
        return
    import pandas as pd

    rows = []
    for level, n_case in [(0, 8), (1, 7), (2, 5), (3, 3), (4, 2)]:  # decreasing -> protective
        rows += _rows_for_level("exercise_level", level, n_case)
    df = pd.DataFrame(rows)

    rm = fit_risk_model(df, "has_htn", ["exercise_level"])
    assert rm.terms.set_index("term").loc["exercise_level"]["odds_ratio"] < 1.0


def test_missing_rows_are_dropped_from_n():
    if _skip_if_no_deps("test_missing_rows_are_dropped_from_n"):
        return
    import pandas as pd

    rows = []
    for level, n_case in [(0, 2), (1, 3), (2, 5), (3, 7), (4, 8)]:
        rows += _rows_for_level("alcohol_level", level, n_case)
    df = pd.DataFrame(rows)
    # two participants with a missing predictor must be excluded (complete-case)
    df = pd.concat([df, pd.DataFrame([{"alcohol_level": pd.NA, "has_htn": 1},
                                      {"alcohol_level": pd.NA, "has_htn": 0}])], ignore_index=True)

    rm = fit_risk_model(df, "has_htn", ["alcohol_level"])
    assert rm.n == 50  # the two NA rows dropped


def test_multivariable_and_categorical_terms_present():
    if _skip_if_no_deps("test_multivariable_and_categorical_terms_present"):
        return
    import pandas as pd

    # every (smoking, alcohol) cell has both cases and controls -> neither predictor separates
    cells = [
        ("current", 1, 3, 2), ("current", 2, 3, 2), ("current", 3, 4, 1), ("current", 4, 4, 1),
        ("never", 1, 1, 4), ("never", 2, 1, 4), ("never", 3, 2, 3), ("never", 4, 2, 3),
    ]
    rows = []
    for status, alc, n_case, n_control in cells:
        rows += [{"smoking_status": status, "alcohol_level": alc, "has_htn": 1} for _ in range(n_case)]
        rows += [{"smoking_status": status, "alcohol_level": alc, "has_htn": 0} for _ in range(n_control)]
    df = pd.DataFrame(rows)

    rm = fit_risk_model(df, "has_htn", ["smoking_status", "alcohol_level"], categorical={"smoking_status"})
    assert rm.converged
    terms = set(rm.terms["term"])
    assert any("smoking_status" in t for t in terms)  # categorical encoded
    assert "alcohol_level" in terms


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
