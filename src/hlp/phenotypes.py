"""Build case/control labels from the codebook phenotype definitions.

The 6 phenotype definitions live in ``codebook/phenotypes/``. Both pipelines call into this
module so a definition change propagates to every cohort at once.

Stub: implement loaders/builders as the codebook definitions are finalized (Milestone 2).
"""

from __future__ import annotations

PHENOTYPES = (
    "atrial_fibrillation",
    "prostate_cancer",
    "asthma",
    "hypertension",
    "colorectal_cancer",
    "breast_cancer",
)


def load_definition(name: str):
    """Load a phenotype definition from codebook/phenotypes/<name>.md. (to implement)"""
    raise NotImplementedError
