"""Tests for src/hlp/linkage.py.

The Hillsborough Health Survey has no sex field; sex for the sex-restricted phenotypes
(prostate, breast) comes from UUID linkage to the master sheet. These verify the sex
normalizer (stdlib) and the attach_sex join (pandas; skips if unavailable), including the
payoff: after linkage, the survey classifier labels prostate/breast correctly and excludes
unknown-sex participants.

Run: python -m pytest tests/ -q   (or: python tests/test_linkage.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.linkage import attach_sex, normalize_sex  # noqa: E402


# --- normalize_sex: canonicalize the master sheet's sex representation ------------------------
def test_normalize_sex_text_variants():
    assert normalize_sex("Male") == "male"
    assert normalize_sex("female") == "female"
    assert normalize_sex(" M ") == "male"
    assert normalize_sex("F") == "female"


def test_normalize_sex_omop_concept_ids():
    # the rest of the codebase speaks OMOP gender concepts; accept them too
    assert normalize_sex(8507) == "male"
    assert normalize_sex(8532) == "female"
    assert normalize_sex("8507.0") == "male"  # pandas may hand us a float-y string


def test_normalize_sex_unknown_is_none():
    for v in ("unknown", "other", "intersex", "U", "", "  ", None):
        assert normalize_sex(v) is None, v


# --- attach_sex: join master-sheet sex onto the survey cohort ---------------------------------
def test_attach_sex_maps_and_normalizes():
    try:
        import pandas as pd
    except ImportError:
        print("SKIP test_attach_sex_maps_and_normalizes (pandas not installed)")
        return

    survey = pd.DataFrame({"participant_id": ["u1", "u2", "u3"]})
    master = pd.DataFrame({"participant_id": ["u1", "u2"], "sex": ["Male", "F"]})
    out = attach_sex(survey, master)

    assert list(out["participant_id"]) == ["u1", "u2", "u3"]
    assert out.set_index("participant_id").loc["u1", "sex"] == "male"
    assert out.set_index("participant_id").loc["u2", "sex"] == "female"
    # u3 is not in the master sheet -> unmatched -> missing sex
    assert pd.isna(out.set_index("participant_id").loc["u3", "sex"])


def test_attach_sex_feeds_survey_classifier():
    """Payoff: after linkage, prostate/breast label correctly and unknown sex is excluded."""
    try:
        import pandas as pd
    except ImportError:
        print("SKIP test_attach_sex_feeds_survey_classifier (pandas not installed)")
        return

    from hlp.survey_phenotypes import build_survey_label_matrix

    survey = pd.DataFrame(
        [
            {"participant_id": "u1", "diagnosed_cancer": "Yes", "cancer_specify": "prostate",
             "diagnosed_highbloodpressure": "Yes", "diagnosed_respiratoryissues": "No"},
            {"participant_id": "u2", "diagnosed_cancer": "Yes", "cancer_specify": "breast",
             "diagnosed_highbloodpressure": "No", "diagnosed_respiratoryissues": "No"},
            {"participant_id": "u3", "diagnosed_cancer": "Yes", "cancer_specify": "prostate",
             "diagnosed_highbloodpressure": "No", "diagnosed_respiratoryissues": "No"},
        ]
    )
    # u1 male, u2 female, u3 not in master (unknown sex)
    master = pd.DataFrame({"participant_id": ["u1", "u2"], "sex": ["M", "Female"]})

    linked = attach_sex(survey, master)
    m = build_survey_label_matrix(linked)

    def val(pid, col):
        v = m.loc[pid, col]
        return None if pd.isna(v) else int(v)

    assert val("u1", "has_prostate_cancer") == 1        # male + prostate specify -> case
    assert val("u2", "has_breast_cancer") == 1          # female + breast specify -> case
    assert val("u1", "has_breast_cancer") is None       # male excluded from breast
    assert val("u3", "has_prostate_cancer") is None     # unknown sex -> excluded from prostate
    assert val("u3", "has_hypertension") == 0           # non-restricted phenotype still labels


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
