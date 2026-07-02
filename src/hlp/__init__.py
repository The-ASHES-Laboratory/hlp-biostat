"""hlp-biostat shared analysis logic.

Environment-agnostic helpers imported by both the AoU (cloud) and Hazel (HPC) entrypoints.
Keeping this logic here (rather than inline in notebooks) is what keeps the Hillsborough and
national cohorts comparable.
"""

__version__ = "0.0.1"

from hlp.phenotypes import (
    PhenotypeDef,
    build_label_matrix,
    build_labels,
    classify_person,
    load_definitions,
)
from hlp.survey_phenotypes import (
    SurveyRule,
    build_survey_label_matrix,
    build_survey_labels,
    classify_person_survey,
    load_survey_rules,
)
from hlp.linkage import (
    attach_sex,
    normalize_sex,
)
from hlp.lifestyle import (
    alcohol_level,
    derive_lifestyle_features,
    exercise_level,
    sleep_level,
    smoking_status,
)
from hlp.compare import (
    Prevalence,
    compare_groups,
    prevalence,
    prevalence_by_group,
    two_by_two,
)

__all__ = [
    "PhenotypeDef",
    "build_label_matrix",
    "build_labels",
    "classify_person",
    "load_definitions",
    "SurveyRule",
    "build_survey_label_matrix",
    "build_survey_labels",
    "classify_person_survey",
    "load_survey_rules",
    "attach_sex",
    "normalize_sex",
    "alcohol_level",
    "derive_lifestyle_features",
    "exercise_level",
    "sleep_level",
    "smoking_status",
    "Prevalence",
    "compare_groups",
    "prevalence",
    "prevalence_by_group",
    "two_by_two",
]
