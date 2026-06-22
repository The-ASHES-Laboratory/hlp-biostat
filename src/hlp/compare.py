"""Cross-group / cross-cohort phenotype comparison statistics.

Compares phenotype prevalence between two groups from the ``has_<phenotype>`` label matrix that
``hlp.phenotypes.build_label_matrix`` produces. Two uses:

- African American (race 8516) vs European American (8527) WITHIN the AoU cohort.
- Hillsborough vs national, once both cohorts are labeled with the same definitions.

The pure-Python core (``prevalence``, ``two_by_two``) is stdlib-only and testable anywhere. The
DataFrame wrappers and Fisher's exact test import pandas / scipy lazily, so importing this module
never requires them.

Labels follow the project convention: 1 = case, 0 = control, None/<NA> = missing/excluded. Missing
labels are dropped from denominators (so sex-restricted phenotypes compare only eligible people).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class Prevalence:
    """Case count and denominator (non-missing) for one phenotype in one group."""

    cases: int
    n: int

    @property
    def prevalence(self) -> float:
        return self.cases / self.n if self.n else float("nan")

    @property
    def controls(self) -> int:
        return self.n - self.cases


def prevalence(labels: Iterable[Optional[int]]) -> Prevalence:
    """Count cases and non-missing total from an iterable of 1/0/None labels."""
    cases = 0
    n = 0
    for v in labels:
        if v is None:
            continue
        n += 1
        if int(v) == 1:
            cases += 1
    return Prevalence(cases=cases, n=n)


def two_by_two(
    labels_a: Iterable[Optional[int]], labels_b: Iterable[Optional[int]]
) -> tuple[int, int, int, int]:
    """Return (a_cases, a_controls, b_cases, b_controls) for a 2x2 case/control x group table."""
    pa = prevalence(labels_a)
    pb = prevalence(labels_b)
    return pa.cases, pa.controls, pb.cases, pb.controls


def _to_label_list(series) -> list[Optional[int]]:
    """Convert a pandas Series (possibly with <NA>) to a list of 1/0/None."""
    import pandas as pd

    return [None if pd.isna(v) else int(v) for v in series]


def prevalence_by_group(label_matrix, group_series, *, phenotype_prefix: str = "has_"):
    """Tidy prevalence table: one row per (phenotype, group).

    ``label_matrix``: DataFrame indexed by person_id with has_<phenotype> columns (1/0/<NA>).
    ``group_series``: Series indexed by person_id giving each person's group label.
    Returns a DataFrame: phenotype, group, cases, n, prevalence.
    """
    import pandas as pd

    groups = group_series.dropna()
    pheno_cols = [c for c in label_matrix.columns if c.startswith(phenotype_prefix)]
    rows = []
    for group_value, members in groups.groupby(groups):
        ids = members.index
        sub = label_matrix.reindex(ids)
        for col in pheno_cols:
            p = prevalence(_to_label_list(sub[col]))
            rows.append(
                {
                    "phenotype": col[len(phenotype_prefix):],
                    "group": group_value,
                    "cases": p.cases,
                    "n": p.n,
                    "prevalence": p.prevalence,
                }
            )
    return pd.DataFrame(rows)


def compare_groups(
    label_matrix,
    group_series,
    group_a,
    group_b,
    *,
    phenotype_prefix: str = "has_",
):
    """Compare phenotype prevalence between two groups with Fisher's exact test.

    Fisher's exact is used (not a z-test) because cohorts here are small (Hillsborough n~62), where
    the normal approximation is unreliable. Returns one row per phenotype:
    phenotype, n_a, cases_a, prev_a, n_b, cases_b, prev_b, prevalence_diff, odds_ratio, p_value.
    ``prevalence_diff`` is prev_a - prev_b.
    """
    import pandas as pd
    from scipy.stats import fisher_exact

    a_ids = group_series[group_series == group_a].index
    b_ids = group_series[group_series == group_b].index
    a_mat = label_matrix.reindex(a_ids)
    b_mat = label_matrix.reindex(b_ids)

    pheno_cols = [c for c in label_matrix.columns if c.startswith(phenotype_prefix)]
    rows = []
    for col in pheno_cols:
        a_cases, a_controls, b_cases, b_controls = two_by_two(
            _to_label_list(a_mat[col]), _to_label_list(b_mat[col])
        )
        odds_ratio, p_value = fisher_exact([[a_cases, a_controls], [b_cases, b_controls]])
        pa = a_cases / (a_cases + a_controls) if (a_cases + a_controls) else float("nan")
        pb = b_cases / (b_cases + b_controls) if (b_cases + b_controls) else float("nan")
        rows.append(
            {
                "phenotype": col[len(phenotype_prefix):],
                "n_a": a_cases + a_controls,
                "cases_a": a_cases,
                "prev_a": pa,
                "n_b": b_cases + b_controls,
                "cases_b": b_cases,
                "prev_b": pb,
                "prevalence_diff": pa - pb,
                "odds_ratio": odds_ratio,
                "p_value": p_value,
            }
        )
    return pd.DataFrame(rows)
