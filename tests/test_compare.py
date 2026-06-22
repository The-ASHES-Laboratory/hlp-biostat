"""Tests for src/hlp/compare.py. Pure-core tests are stdlib-only; the DataFrame/Fisher test skips
without pandas+scipy.

Run: python tests/test_compare.py   (or pytest tests/)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.compare import prevalence, two_by_two  # noqa: E402


def test_prevalence_skips_missing():
    p = prevalence([1, 0, 1, None, 0])
    assert p.cases == 2
    assert p.n == 4  # None dropped
    assert p.controls == 2
    assert abs(p.prevalence - 0.5) < 1e-9


def test_prevalence_all_missing_is_nan():
    p = prevalence([None, None])
    assert p.cases == 0 and p.n == 0
    assert p.prevalence != p.prevalence  # NaN


def test_two_by_two():
    # group A: 2 cases / 1 control ; group B: 1 case / 2 controls (one None dropped)
    a_cases, a_controls, b_cases, b_controls = two_by_two([1, 1, 0], [1, 0, 0, None])
    assert (a_cases, a_controls, b_cases, b_controls) == (2, 1, 1, 2)


def test_compare_groups_wrapper():
    """DataFrame + Fisher wrapper. Skips without pandas+scipy."""
    try:
        import pandas as pd
        import scipy  # noqa: F401
    except ImportError:
        print("SKIP test_compare_groups_wrapper (pandas/scipy not installed)")
        return

    from hlp.compare import compare_groups, prevalence_by_group

    # 6 people, one phenotype; group AA has higher prevalence than EA
    label_matrix = pd.DataFrame(
        {"has_hypertension": pd.array([1, 1, 0, 0, 0, 1], dtype="Int64")},
        index=[1, 2, 3, 4, 5, 6],
    )
    group = pd.Series(["AA", "AA", "AA", "EA", "EA", "EA"], index=[1, 2, 3, 4, 5, 6])

    by_group = prevalence_by_group(label_matrix, group)
    aa = by_group[(by_group.group == "AA") & (by_group.phenotype == "hypertension")].iloc[0]
    ea = by_group[(by_group.group == "EA") & (by_group.phenotype == "hypertension")].iloc[0]
    assert aa.cases == 2 and aa.n == 3
    assert ea.cases == 1 and ea.n == 3

    cmp = compare_groups(label_matrix, group, "AA", "EA")
    row = cmp.iloc[0]
    assert row.phenotype == "hypertension"
    assert row.cases_a == 2 and row.n_a == 3
    assert row.cases_b == 1 and row.n_b == 3
    assert abs(row.prevalence_diff - (2 / 3 - 1 / 3)) < 1e-9
    assert 0.0 <= row.p_value <= 1.0


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
