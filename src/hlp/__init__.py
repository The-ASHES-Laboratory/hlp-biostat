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

__all__ = [
    "PhenotypeDef",
    "build_label_matrix",
    "build_labels",
    "classify_person",
    "load_definitions",
]
