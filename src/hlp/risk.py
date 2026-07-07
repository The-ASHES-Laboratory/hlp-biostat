"""Logistic risk models: phenotype ~ lifestyle + demographics.

The analytical payoff for the Hillsborough cohort. Takes a per-participant frame that carries a
binary phenotype label (from ``phenotypes`` / ``survey_phenotypes``) and covariates (from
``lifestyle`` plus demographics) and fits a logistic regression, reporting adjusted odds ratios
with 95% confidence intervals and p-values per term.

Design notes:
- **Logistic regression** (statsmodels ``Logit`` via the formula API) so categorical covariates
  (e.g. ``smoking_status``) are dummy-encoded automatically. Ordinals (alcohol/exercise/sleep
  levels) are treated as continuous linear trends by default; pass them in ``categorical`` to
  encode them as unordered factors instead.
- **Odds ratio** = exp(coefficient); CI = exp(profile of the coefficient CI).
- **Complete-case**: rows with any missing outcome/covariate are dropped, and ``n`` reports the
  effective sample actually modeled (cohorts here are small, so this matters).
- For full control (custom reference levels, interactions) pass a raw patsy ``formula=``.

statsmodels / pandas are imported lazily, so importing this module never requires them; only
``fit_risk_model`` does. ``build_formula`` is pure/stdlib.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


def build_formula(
    outcome: str,
    predictors: Iterable[str],
    *,
    categorical: Iterable[str] = (),
) -> str:
    """Build a patsy formula ``outcome ~ t1 + t2``, wrapping ``categorical`` predictors in C()."""
    predictors = list(predictors)
    if not predictors:
        raise ValueError("need at least one predictor")
    cat = set(categorical)
    terms = [f"C({p})" if p in cat else p for p in predictors]
    return f"{outcome} ~ " + " + ".join(terms)


@dataclass
class RiskModel:
    """Result of one logistic risk model.

    ``terms`` is a DataFrame with columns: term, odds_ratio, ci_low, ci_high, p_value (one row per
    model term, including the Intercept). ``n`` is the complete-case sample actually modeled.
    """

    outcome: str
    terms: object  # pandas DataFrame
    n: int
    n_cases: int
    n_controls: int
    converged: bool


def fit_risk_model(
    df,
    outcome: str,
    predictors: Iterable[str],
    *,
    categorical: Iterable[str] = (),
    formula: Optional[str] = None,
) -> RiskModel:
    """Fit a logistic risk model and return odds ratios with CIs (pandas + statsmodels).

    Parameters
    ----------
    df          : per-participant frame with the outcome and predictor columns.
    outcome     : name of the 0/1 phenotype column.
    predictors  : covariate column names.
    categorical : predictors to dummy-encode (wrapped in C()); others enter as continuous.
    formula     : optional raw patsy formula overriding ``outcome``/``predictors``/``categorical``.
    """
    import warnings

    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf
    from statsmodels.tools.sm_exceptions import (
        ConvergenceWarning,
        PerfectSeparationError,
        PerfectSeparationWarning,
    )

    predictors = list(predictors)
    cat = set(categorical)
    if formula is None:
        formula = build_formula(outcome, predictors, categorical=cat)

    # Assemble a complete-case frame: numeric columns coerced (nullable NA -> NaN), categoricals
    # left as strings, then drop any row with a missing outcome/covariate.
    cols = [outcome] + predictors
    data = df[cols].copy()
    for c in cols:
        if c in cat:
            data[c] = data[c].astype("object")
        else:
            data[c] = pd.to_numeric(data[c], errors="coerce").astype(float)
    data = data.dropna(subset=cols)

    n = len(data)
    y = data[outcome]
    n_cases = int((y == 1).sum())
    n_controls = int((y == 0).sum())

    try:
        with warnings.catch_warnings():
            # Non-convergence / quasi-separation at small n is surfaced structurally via the
            # `converged` flag below, not as console noise. (A near-constant covariate at n~48 -
            # e.g. a 93%-prevalent family history - will do this.)
            warnings.simplefilter("ignore", ConvergenceWarning)
            warnings.simplefilter("ignore", PerfectSeparationWarning)
            res = smf.logit(formula, data=data).fit(disp=0)
    except PerfectSeparationError as exc:
        raise ValueError(
            f"perfect separation fitting '{outcome}' (n={n}, cases={n_cases}); "
            f"cohort too small or a covariate separates the outcome: {exc}"
        )
    converged = bool(res.mle_retvals.get("converged", True))

    conf = res.conf_int()
    with np.errstate(over="ignore"):  # a separated fit yields an inf OR - meaningful, not a warning
        terms = pd.DataFrame(
            {
                "term": list(res.params.index),
                "odds_ratio": np.exp(res.params.to_numpy()),
                "ci_low": np.exp(conf.iloc[:, 0].to_numpy()),
                "ci_high": np.exp(conf.iloc[:, 1].to_numpy()),
                "p_value": res.pvalues.to_numpy(),
            }
        )
    return RiskModel(
        outcome=outcome,
        terms=terms,
        n=n,
        n_cases=n_cases,
        n_controls=n_controls,
        converged=converged,
    )
