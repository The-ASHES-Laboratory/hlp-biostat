#!/usr/bin/env python
"""Descriptive + exploratory summary of the Hillsborough combo-summaries cohort.

Reads the local, gitignored ``data/HLP_Combo_summaries.xlsx`` (IRB #27626), maps it via
``hlp.hillsborough``, and reports prevalences, lifestyle distributions, an exploratory risk
model (with family history), and an African-American-only subset. Aggregates only - no
participant rows. Run in the ``hlp-biostat`` env:

    python analysis/hillsborough_summary.py

The full report is also written to ``data/outputs/`` (gitignored), so real numbers stay local.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.hillsborough import DATA_DIR, build_features, load_combo_summaries  # noqa: E402
from hlp.risk import fit_risk_model  # noqa: E402

PHENOTYPES = ["has_hypertension", "has_asthma", "has_any_cancer"]
LIFESTYLE = ["ever_smoked", "drinks", "regular_exercise", "adequate_sleep", "pollutant_exposure"]


def _prev(series):
    cases = int((series == 1).sum())
    n = int(series.notna().sum())
    pct = 100 * cases / n if n else float("nan")
    return cases, n, pct


def summarize(f, *, label: str) -> list[str]:
    """Descriptive lines (demographics + prevalence + lifestyle) for a feature frame."""
    out = [f"\n=== {label} (n={len(f)}) ===", "-- Demographics --",
           f"sex: {dict(f['sex'].value_counts(dropna=False))}",
           f"age: mean={f['age'].mean():.1f}, range={f['age'].min():.0f}-{f['age'].max():.0f}"]
    out.append("-- Phenotype prevalence --")
    for col in PHENOTYPES:
        cases, nn, pct = _prev(f[col])
        flag = "  [UNDERPOWERED n<5]" if cases < 5 else ""
        out.append(f"  {col:20s}: {cases}/{nn} = {pct:.1f}%{flag}")
    out.append("-- Lifestyle / family history (count of 1 / non-missing) --")
    for col in LIFESTYLE + ["family_hypertension"]:
        out.append(f"  {col:20s}: {int((f[col] == 1).sum())}/{int(f[col].notna().sum())}")
    return out


def model_section(f) -> list[str]:
    out = ["\n-- Exploratory risk model: hypertension ~ age + sex + lifestyle --",
           "   EXPLORATORY ONLY: small n, low events-per-variable; ORs are hypothesis-generating.",
           "   (family_hypertension excluded: near-universal in this cohort, so it quasi-separates",
           "    the fit and carries no discriminative variance at this n - see descriptive count.)"]
    m = f.copy()
    m["sex_female"] = (m["sex"] == "female").astype("Int64")
    predictors = ["age", "sex_female", "regular_exercise", "adequate_sleep"]
    try:
        rm = fit_risk_model(m, "has_hypertension", predictors)
        out.append(f"   n={rm.n}, cases={rm.n_cases}, controls={rm.n_controls}, converged={rm.converged}")
        tbl = rm.terms.copy()
        for c in ("odds_ratio", "ci_low", "ci_high", "p_value"):
            tbl[c] = tbl[c].map(lambda x: f"{x:.3f}")
        out += ["   " + ln for ln in tbl.to_string(index=False).splitlines()]
    except Exception as exc:  # noqa: BLE001
        out.append(f"   model did not fit: {type(exc).__name__}: {exc}")
    return out


def main():
    f = build_features(load_combo_summaries())

    lines = ["Hillsborough combo-summaries analysis (IRB #27626; local only)"]
    lines += summarize(f, label="Full cohort")
    lines += model_section(f)

    aa = f[f["ethnicity"] == "African American"]
    lines += summarize(aa, label="African-American-only subset (descriptive)")
    lines.append("   (subset too small for a stable multivariable model; descriptive only)")

    report = "\n".join(lines)
    print(report)

    out_dir = DATA_DIR / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "hillsborough_summary.txt"
    out_path.write_text(report + "\n")
    print(f"\n[saved -> {out_path} (gitignored)]")


if __name__ == "__main__":
    main()
