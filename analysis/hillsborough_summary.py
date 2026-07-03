#!/usr/bin/env python
"""Descriptive + exploratory summary of the Hillsborough combo-summaries cohort.

Reads the local, gitignored ``data/HLP_Combo_summaries.xlsx`` (IRB #27626), maps it via
``hlp.hillsborough``, and prints prevalences, lifestyle distributions, and one exploratory
risk model. Prints aggregates only - no participant rows. Run in the ``hlp-biostat`` env:

    python analysis/hillsborough_summary.py

Nothing here is committed with real numbers; the sheet and any saved outputs stay under data/.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from hlp.hillsborough import build_features, load_combo_summaries  # noqa: E402
from hlp.risk import fit_risk_model  # noqa: E402

PHENOTYPES = ["has_hypertension", "has_asthma", "has_any_cancer"]
LIFESTYLE = ["ever_smoked", "drinks", "regular_exercise", "adequate_sleep", "pollutant_exposure"]


def _prev(series):
    cases = int((series == 1).sum())
    n = int(series.notna().sum())
    pct = 100 * cases / n if n else float("nan")
    return cases, n, pct


def main():
    df = load_combo_summaries()
    f = build_features(df)
    n = len(f)

    print(f"\n=== Hillsborough combo cohort (n={n}) ===")

    print("\n-- Demographics --")
    print("sex:", dict(f["sex"].value_counts(dropna=False)))
    print(f"age: mean={f['age'].mean():.1f}, range={f['age'].min():.0f}-{f['age'].max():.0f}, missing={f['age'].isna().sum()}")
    print("ethnicity:", dict(f["ethnicity"].value_counts(dropna=False)))

    print("\n-- Phenotype prevalence --")
    for col in PHENOTYPES:
        cases, nn, pct = _prev(f[col])
        flag = "  [UNDERPOWERED n<5; not comparable to AoU subtypes]" if col == "has_any_cancer" else ""
        print(f"{col:20s}: {cases}/{nn} = {pct:.1f}%{flag}")

    print("\n-- Lifestyle (count of 1 / non-missing) --")
    for col in LIFESTYLE:
        ones = int((f[col] == 1).sum())
        nn = int(f[col].notna().sum())
        print(f"{col:20s}: {ones}/{nn}")

    print("\n-- Exploratory risk model (hypertension ~ age + sex + lifestyle) --")
    print("   EXPLORATORY ONLY: small n, low events-per-variable; treat ORs as hypothesis-generating.")
    model_df = f.copy()
    model_df["sex_female"] = (model_df["sex"] == "female").astype("Int64")
    predictors = ["age", "sex_female", "ever_smoked", "regular_exercise", "adequate_sleep"]
    try:
        rm = fit_risk_model(model_df, "has_hypertension", predictors)
        print(f"   n={rm.n}, cases={rm.n_cases}, controls={rm.n_controls}, converged={rm.converged}")
        tbl = rm.terms.copy()
        for c in ("odds_ratio", "ci_low", "ci_high", "p_value"):
            tbl[c] = tbl[c].map(lambda x: f"{x:.3f}")
        print(tbl.to_string(index=False))
    except Exception as exc:  # noqa: BLE001
        print(f"   model did not fit: {type(exc).__name__}: {exc}")

    print()


if __name__ == "__main__":
    main()
