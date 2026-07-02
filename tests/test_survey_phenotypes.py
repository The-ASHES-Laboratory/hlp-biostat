"""Tests for the pure-Python core of src/hlp/survey_phenotypes.py.

Hillsborough survey -> case/control labels, mirroring the AoU-side contract in
src/hlp/phenotypes.py (1 case, 0 control, None excluded/missing). Stdlib only; the
pandas wrapper test skips if pandas is unavailable.

Run: python -m pytest tests/ -q   (or: python tests/test_survey_phenotypes.py)
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hlp.survey_phenotypes import (  # noqa: E402
    SurveyRule,
    classify_person_survey,
    load_survey_rules,
)

# --- fixtures: minimal survey rules mirroring the codebook ------------------------------------
HTN = SurveyRule(
    name="hypertension",
    rule_type="direct",
    survey_item="diagnosed_highbloodpressure",
    case_values=frozenset({"yes"}),
    control_values=frozenset({"no"}),
)
AF = SurveyRule(name="atrial_fibrillation", rule_type="not_ascertainable")
COLORECTAL = SurveyRule(
    name="colorectal_cancer",
    rule_type="cancer_freetext",
    survey_item="diagnosed_cancer",
    case_values=frozenset({"yes"}),
    control_values=frozenset({"no"}),
    cancer_keywords=frozenset({"colorectal", "colon", "rectal", "rectum", "bowel"}),
)
PROSTATE = SurveyRule(
    name="prostate_cancer",
    rule_type="cancer_freetext",
    survey_item="diagnosed_cancer",
    case_values=frozenset({"yes"}),
    control_values=frozenset({"no"}),
    cancer_keywords=frozenset({"prostate"}),
    sex_restriction="male",
)
BREAST = SurveyRule(
    name="breast_cancer",
    rule_type="cancer_freetext",
    survey_item="diagnosed_cancer",
    case_values=frozenset({"yes"}),
    control_values=frozenset({"no"}),
    cancer_keywords=frozenset({"breast"}),
    sex_restriction="female",
)


# --- direct self-report items ----------------------------------------------------------------
def test_direct_yes_is_case_no_is_control():
    assert classify_person_survey({"diagnosed_highbloodpressure": "Yes"}, HTN) == 1
    assert classify_person_survey({"diagnosed_highbloodpressure": "No"}, HTN) == 0


def test_direct_unsure_or_missing_is_none():
    assert classify_person_survey({"diagnosed_highbloodpressure": "Unsure"}, HTN) is None
    assert classify_person_survey({"diagnosed_highbloodpressure": "Prefer not to answer"}, HTN) is None
    assert classify_person_survey({}, HTN) is None


def test_direct_normalizes_case_and_whitespace():
    assert classify_person_survey({"diagnosed_highbloodpressure": " yes "}, HTN) == 1
    assert classify_person_survey({"diagnosed_highbloodpressure": "NO"}, HTN) == 0


# --- not ascertainable (AF) ------------------------------------------------------------------
def test_not_ascertainable_always_none():
    assert classify_person_survey({"diagnosed_cardiovascularcondition": "Yes"}, AF) is None
    assert classify_person_survey({}, AF) is None


# --- cancer gateway + free-text specify ------------------------------------------------------
def test_cancer_no_gateway_is_control():
    assert classify_person_survey({"diagnosed_cancer": "No"}, COLORECTAL) == 0


def test_cancer_yes_matching_specify_is_case():
    r = {"diagnosed_cancer": "Yes", "cancer_specify": "colon cancer"}
    assert classify_person_survey(r, COLORECTAL) == 1


def test_cancer_yes_different_type_excluded_from_controls():
    # has a cancer, but not colorectal -> excluded (None), NOT a control
    r = {"diagnosed_cancer": "Yes", "cancer_specify": "lung cancer"}
    assert classify_person_survey(r, COLORECTAL) is None


def test_cancer_yes_empty_specify_is_excluded():
    r = {"diagnosed_cancer": "Yes", "cancer_specify": ""}
    assert classify_person_survey(r, COLORECTAL) is None


def test_cancer_gateway_pna_is_none():
    assert classify_person_survey({"diagnosed_cancer": "Prefer not to answer"}, COLORECTAL) is None


def test_cancer_multiple_types_in_freetext():
    r = {"diagnosed_cancer": "Yes", "cancer_specify": "breast and colon"}
    assert classify_person_survey(r, COLORECTAL, sex="female") == 1
    assert classify_person_survey(r, BREAST, sex="female") == 1
    assert classify_person_survey(r, PROSTATE, sex="male") is None  # no prostate in text


# --- sex restriction (mirrors AoU semantics) -------------------------------------------------
def test_sex_restriction_excludes_wrong_sex():
    male_prostate = {"diagnosed_cancer": "Yes", "cancer_specify": "prostate cancer"}
    assert classify_person_survey(male_prostate, PROSTATE, sex="male") == 1
    assert classify_person_survey(male_prostate, PROSTATE, sex="female") is None
    # a female with no cancer is an eligible breast-cancer control; a male is excluded
    assert classify_person_survey({"diagnosed_cancer": "No"}, BREAST, sex="female") == 0
    assert classify_person_survey({"diagnosed_cancer": "No"}, BREAST, sex="male") is None


def test_sex_unknown_excluded_when_restricted():
    r = {"diagnosed_cancer": "Yes", "cancer_specify": "prostate"}
    assert classify_person_survey(r, PROSTATE, sex=None) is None


# --- validation ------------------------------------------------------------------------------
def test_surveyrule_validation():
    try:
        SurveyRule(name="x", rule_type="bogus")
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for bad rule_type")

    try:
        SurveyRule(
            name="x", rule_type="cancer_freetext", survey_item="diagnosed_cancer",
            case_values=frozenset({"yes"}), control_values=frozenset({"no"}),
            cancer_keywords=frozenset(), sex_restriction="other",
        )
    except ValueError:
        pass
    else:  # pragma: no cover
        raise AssertionError("expected ValueError for bad sex_restriction")


# --- integration: load real codebook survey_rules.csv ----------------------------------------
def test_load_survey_rules_from_codebook():
    rules = load_survey_rules()
    assert set(rules) == {
        "asthma", "hypertension", "atrial_fibrillation",
        "colorectal_cancer", "prostate_cancer", "breast_cancer",
    }
    assert rules["hypertension"].rule_type == "direct"
    assert rules["atrial_fibrillation"].rule_type == "not_ascertainable"
    assert rules["colorectal_cancer"].rule_type == "cancer_freetext"
    assert rules["prostate_cancer"].sex_restriction == "male"
    assert rules["breast_cancer"].sex_restriction == "female"
    # cancer rules carry keywords; direct/not-ascertainable do not
    assert rules["colorectal_cancer"].cancer_keywords
    assert not rules["hypertension"].cancer_keywords


# --- pandas wrapper --------------------------------------------------------------------------
def test_build_survey_label_matrix_wrapper():
    """AF dropped by default; direct + cancer rules produce has_<pheno> columns matching AoU side."""
    try:
        import pandas as pd
    except ImportError:
        print("SKIP test_build_survey_label_matrix_wrapper (pandas not installed)")
        return

    from hlp.survey_phenotypes import build_survey_label_matrix

    survey = pd.DataFrame(
        [
            {"participant_id": "u1", "sex": "male", "diagnosed_highbloodpressure": "Yes",
             "diagnosed_respiratoryissues": "No", "diagnosed_cancer": "Yes", "cancer_specify": "prostate"},
            {"participant_id": "u2", "sex": "female", "diagnosed_highbloodpressure": "No",
             "diagnosed_respiratoryissues": "Yes", "diagnosed_cancer": "No", "cancer_specify": ""},
            {"participant_id": "u3", "sex": "female", "diagnosed_highbloodpressure": "Unsure",
             "diagnosed_respiratoryissues": "No", "diagnosed_cancer": "Yes", "cancer_specify": "breast cancer"},
        ]
    )
    m = build_survey_label_matrix(survey)

    def val(pid, col):
        v = m.loc[pid, col]
        return None if pd.isna(v) else int(v)

    # AF is not ascertainable -> dropped from the matrix
    assert "has_atrial_fibrillation" not in m.columns
    assert val("u1", "has_hypertension") == 1
    assert val("u1", "has_prostate_cancer") == 1
    assert val("u2", "has_asthma") == 1
    assert val("u2", "has_breast_cancer") == 0        # female, no cancer -> control
    assert val("u1", "has_breast_cancer") is None     # male excluded from breast
    assert val("u3", "has_hypertension") is None      # Unsure -> missing
    assert val("u3", "has_breast_cancer") == 1


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
