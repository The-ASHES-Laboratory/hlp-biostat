"""Build case/control labels from the codebook phenotype definitions.

The 6 phenotype definitions are the single source of truth in ``codebook/``:

- ``condition_concepts.csv``  : concept_id -> disease_group (the per-phenotype concept set)
- ``phenotype_params.csv``    : per-phenotype case rule (min_occurrences, sex_restriction, ...)
- ``phenotypes/<name>.md``    : human-readable rationale for each definition

Both pipelines (AoU national cohort, Hazel Hillsborough cohort) call into this module, so a
definition change propagates to every cohort at once and keeps the comparison apples-to-apples.

Locked decisions (2026-06-20):
- Case threshold is per-phenotype: >=1 distinct-day code for the three cancers, >=2 for the
  chronic conditions (asthma, hypertension, atrial fibrillation).
- Concept matching is exact (no OMOP descendant expansion yet). ``include_descendants`` is a
  forward hook; expansion needs the in-cloud ``concept_ancestor`` table.
- Sex restriction: prostate -> male only, breast -> female only, applied to cases AND controls.

The core (``classify_person``, ``load_definitions``) is pure-Python and depends only on the
standard library, so it is testable anywhere. ``build_labels`` / ``build_label_matrix`` are thin
pandas wrappers for the pipelines (pandas imported lazily).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

# Repo layout: src/hlp/phenotypes.py -> parents[2] is the repo root.
CODEBOOK_DIR = Path(__file__).resolve().parents[2] / "codebook"
CONDITION_CONCEPTS_CSV = CODEBOOK_DIR / "condition_concepts.csv"
PHENOTYPE_PARAMS_CSV = CODEBOOK_DIR / "phenotype_params.csv"

# OMOP standard concept IDs used across the project.
RACE_AFRICAN_AMERICAN = 8516
RACE_EUROPEAN_AMERICAN = 8527
SEX_CONCEPT = {"male": 8507, "female": 8532}

PHENOTYPES = (
    "atrial_fibrillation",
    "prostate_cancer",
    "asthma",
    "hypertension",
    "colorectal_cancer",
    "breast_cancer",
)


@dataclass(frozen=True)
class PhenotypeDef:
    """A single phenotype's case/control definition, assembled from the codebook."""

    name: str
    concept_ids: frozenset[int]
    min_occurrences: int = 1
    sex_restriction: Optional[str] = None  # None | "male" | "female"
    include_descendants: bool = False

    def __post_init__(self) -> None:
        if self.sex_restriction not in (None, "male", "female"):
            raise ValueError(
                f"{self.name}: sex_restriction must be None/'male'/'female', "
                f"got {self.sex_restriction!r}"
            )
        if self.min_occurrences < 1:
            raise ValueError(f"{self.name}: min_occurrences must be >= 1")
        if self.include_descendants:
            # Exact match is the locked behavior; descendant expansion is not implemented yet.
            # When enabled, expansion must happen at load time (concept_ids already expanded).
            raise NotImplementedError(
                f"{self.name}: descendant expansion needs the in-cloud concept_ancestor table; "
                "expand concept_ids at load time before constructing the definition."
            )

    @property
    def sex_concept_id(self) -> Optional[int]:
        return None if self.sex_restriction is None else SEX_CONCEPT[self.sex_restriction]


def _parse_bool(value: str) -> bool:
    return str(value).strip().lower() in ("1", "true", "yes", "y")


def load_definitions(
    concepts_csv: Path = CONDITION_CONCEPTS_CSV,
    params_csv: Path = PHENOTYPE_PARAMS_CSV,
) -> dict[str, PhenotypeDef]:
    """Assemble every phenotype definition from the two codebook CSVs.

    Raises if a phenotype has parameters but no concept set (or vice versa), so a half-finished
    codebook fails loudly rather than silently building an empty phenotype.
    """
    # concept_id -> disease_group, grouped into per-phenotype sets.
    concept_sets: dict[str, set[int]] = {}
    with open(concepts_csv, newline="") as fh:
        for row in csv.DictReader(fh):
            group = (row.get("disease_group") or "").strip()
            cid = (row.get("concept_id") or "").strip()
            if not group or not cid:
                continue
            concept_sets.setdefault(group, set()).add(int(cid))

    definitions: dict[str, PhenotypeDef] = {}
    seen_params: set[str] = set()
    with open(params_csv, newline="") as fh:
        for row in csv.DictReader(fh):
            name = (row.get("phenotype") or "").strip()
            if not name:
                continue
            seen_params.add(name)
            if name not in concept_sets:
                raise ValueError(f"phenotype '{name}' has params but no concepts in {concepts_csv.name}")
            sex = (row.get("sex_restriction") or "").strip() or None
            definitions[name] = PhenotypeDef(
                name=name,
                concept_ids=frozenset(concept_sets[name]),
                min_occurrences=int(row.get("min_occurrences") or 1),
                sex_restriction=sex,
                include_descendants=_parse_bool(row.get("include_descendants") or "false"),
            )

    missing_params = set(concept_sets) - seen_params
    if missing_params:
        raise ValueError(
            f"concept sets without phenotype_params rows: {sorted(missing_params)}"
        )
    return definitions


def classify_person(
    gender_concept_id: Optional[int],
    records: Iterable[tuple[int, object]],
    definition: PhenotypeDef,
) -> Optional[int]:
    """Classify one person for one phenotype.

    Parameters
    ----------
    gender_concept_id : the person's OMOP gender concept id (8507 male, 8532 female), or None.
    records           : iterable of (condition_concept_id, day) for this person. ``day`` is any
                        hashable representing the occurrence date; distinct days are counted, so a
                        repeated code on the same day counts once (this is what makes >=2 mean two
                        separate-day diagnoses).
    definition        : the PhenotypeDef.

    Returns
    -------
    1  : case
    0  : control
    None : excluded (sex restriction excludes this person from both cases and controls)
    """
    if definition.sex_restriction is not None and gender_concept_id != definition.sex_concept_id:
        return None
    qualifying_days = {day for cid, day in records if cid in definition.concept_ids}
    return 1 if len(qualifying_days) >= definition.min_occurrences else 0


def build_labels(
    condition_df,
    person_df,
    definition: PhenotypeDef,
    *,
    person_id_col: str = "person_id",
    concept_col: str = "condition_concept_id",
    date_col: str = "condition_start_date",
    gender_col: str = "gender_concept_id",
):
    """Build a case/control label Series for one phenotype over a cohort (pandas wrapper).

    Returns a pandas ``Int64`` Series indexed by person_id: 1 case, 0 control, <NA> excluded
    (sex-restricted out). The cohort population is taken from ``person_df`` (one row per person),
    so people with zero condition records are correctly labeled controls.
    """
    import pandas as pd

    persons = person_df[[person_id_col, gender_col]].drop_duplicates(person_id_col)
    if definition.sex_restriction is not None:
        persons = persons[persons[gender_col] == definition.sex_concept_id]
    eligible_ids = persons[person_id_col]

    qualifying = condition_df[condition_df[concept_col].isin(definition.concept_ids)].copy()
    qualifying["_day"] = pd.to_datetime(qualifying[date_col], errors="coerce").dt.date
    distinct_days = qualifying.groupby(person_id_col)["_day"].nunique()
    case_ids = set(distinct_days[distinct_days >= definition.min_occurrences].index)

    labels = eligible_ids.map(lambda pid: 1 if pid in case_ids else 0)
    series = pd.Series(labels.values, index=eligible_ids.values, name=f"has_{definition.name}")
    return series.astype("Int64")


def build_label_matrix(
    condition_df,
    person_df,
    definitions: Optional[dict[str, PhenotypeDef]] = None,
    **kwargs,
):
    """Build a person_id x has_<phenotype> matrix for all phenotypes (pandas wrapper).

    Column names match the notebook convention (``has_asthma``, ``has_hypertension``, ...), so the
    PLINK phenotype-file step can consume this directly.
    """
    import pandas as pd

    if definitions is None:
        definitions = load_definitions()
    columns = {
        f"has_{name}": build_labels(condition_df, person_df, d, **kwargs)
        for name, d in definitions.items()
    }
    return pd.DataFrame(columns)
