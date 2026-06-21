"""Tests for the pure-Python core of src/hlp/phenotypes.py.

Stdlib only (no pandas), so they run anywhere. The pandas wrappers (build_labels,
build_label_matrix) mirror this logic and are exercised in the pipeline environments.

Run: python -m pytest tests/ -q   (or: python tests/test_phenotypes.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.phenotypes import (  # noqa: E402
    PhenotypeDef,
    classify_person,
    load_definitions,
)

# --- fixtures: minimal phenotype defs mirroring the locked decisions ---------------------------
ASTHMA = PhenotypeDef(name="asthma", concept_ids=frozenset({317009, 256448}), min_occurrences=2)
PROSTATE = PhenotypeDef(
    name="prostate_cancer", concept_ids=frozenset({4163261}), min_occurrences=1, sex_restriction="male"
)
BREAST = PhenotypeDef(
    name="breast_cancer", concept_ids=frozenset({4155468}), min_occurrences=1, sex_restriction="female"
)

MALE, FEMALE = 8507, 8532


def test_chronic_requires_two_distinct_days():
    # one code -> control; two codes same day -> still control; two distinct days -> case
    assert classify_person(FEMALE, [(317009, "2020-01-01")], ASTHMA) == 0
    assert classify_person(FEMALE, [(317009, "2020-01-01"), (256448, "2020-01-01")], ASTHMA) == 0
    assert classify_person(FEMALE, [(317009, "2020-01-01"), (256448, "2020-02-01")], ASTHMA) == 1


def test_cancer_single_code_is_case():
    assert classify_person(MALE, [(4163261, "2019-05-05")], PROSTATE) == 1
    assert classify_person(MALE, [], PROSTATE) == 0


def test_non_matching_concept_does_not_count():
    assert classify_person(FEMALE, [(999999, "2020-01-01"), (888888, "2020-02-01")], ASTHMA) == 0


def test_sex_restriction_excludes_wrong_sex():
    # female with a prostate code is EXCLUDED (None), not a case and not a control
    assert classify_person(FEMALE, [(4163261, "2019-05-05")], PROSTATE) is None
    # male is eligible as a control for breast
    assert classify_person(MALE, [], BREAST) is None
    assert classify_person(FEMALE, [], BREAST) == 0


def test_unknown_gender_excluded_when_restricted():
    assert classify_person(None, [(4163261, "2019-05-05")], PROSTATE) is None


def test_phenotypedef_validation():
    try:
        PhenotypeDef(name="x", concept_ids=frozenset({1}), sex_restriction="other")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for bad sex_restriction")

    try:
        PhenotypeDef(name="x", concept_ids=frozenset({1}), include_descendants=True)
    except NotImplementedError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected NotImplementedError for descendant expansion")


def test_load_definitions_from_codebook():
    """Integration: the real codebook CSVs assemble into 6 valid definitions with locked params."""
    defs = load_definitions()
    assert set(defs) == {
        "asthma", "hypertension", "atrial_fibrillation",
        "colorectal_cancer", "prostate_cancer", "breast_cancer",
    }
    # locked thresholds
    assert defs["asthma"].min_occurrences == 2
    assert defs["hypertension"].min_occurrences == 2
    assert defs["atrial_fibrillation"].min_occurrences == 2
    assert defs["colorectal_cancer"].min_occurrences == 1
    # locked sex restrictions
    assert defs["prostate_cancer"].sex_restriction == "male"
    assert defs["breast_cancer"].sex_restriction == "female"
    assert defs["asthma"].sex_restriction is None
    # concept sets are non-empty
    assert defs["prostate_cancer"].concept_ids
    assert 4163261 in defs["prostate_cancer"].concept_ids


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
