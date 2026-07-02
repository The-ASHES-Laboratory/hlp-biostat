"""Link master-sheet metadata onto the Hillsborough survey cohort.

The Health Survey carries no sex field (see codebook/survey_variables.csv), but two phenotypes are
sex-restricted (prostate -> male, breast -> female). Sex is resolved by UUID linkage to the lab
master sheet, which stays on the encrypted drive and is joined in at analysis time. This module is
the seam: ``normalize_sex`` canonicalizes whatever the master sheet records, and ``attach_sex``
joins it onto the survey frame as a ``sex`` column that ``survey_phenotypes`` consumes.

Conservative by design: any sex value that is not unambiguously male/female (unknown, other, blank,
or a participant missing from the master sheet) normalizes to ``None``. For the sex-restricted
phenotypes that means the participant is excluded rather than guessed, which is the safe default for
a case/control label. Non-restricted phenotypes (hypertension, asthma, colorectal) are unaffected.

``normalize_sex`` is pure-Python / stdlib. ``attach_sex`` is a thin pandas join (pandas imported
lazily).
"""

from __future__ import annotations

from typing import Optional

# Accepts free-text master-sheet values and the OMOP gender concepts used elsewhere in the codebase.
_MALE_TOKENS = frozenset({"male", "m", "8507"})
_FEMALE_TOKENS = frozenset({"female", "f", "8532"})


def normalize_sex(value: object) -> Optional[str]:
    """Canonicalize a master-sheet sex value to 'male' / 'female' / None.

    Handles text ("Male", "F", case/whitespace), the OMOP gender concept ids (8507/8532), and
    pandas' float-ish forms ("8507.0", NaN). Anything not unambiguously male/female -> None.
    """
    if value is None:
        return None
    key = str(value).strip().lower()
    if key.endswith(".0"):  # e.g. a pandas int column handed over as 8507.0
        key = key[:-2]
    if key in _MALE_TOKENS:
        return "male"
    if key in _FEMALE_TOKENS:
        return "female"
    return None


def attach_sex(
    survey_df,
    master_df,
    *,
    survey_id_col: str = "participant_id",
    master_id_col: str = "participant_id",
    master_sex_col: str = "sex",
    out_col: str = "sex",
):
    """Join normalized master-sheet sex onto the survey cohort (pandas wrapper).

    Returns a copy of ``survey_df`` with an ``out_col`` sex column ('male'/'female'/<NA>).
    Participants absent from the master sheet (or with an unrecognized sex) get <NA>, which the
    survey classifier treats as excluded for the sex-restricted phenotypes. If the master sheet has
    duplicate ids, the first occurrence wins.
    """
    import pandas as pd

    master = master_df[[master_id_col, master_sex_col]].drop_duplicates(master_id_col)
    sex_map = {
        row[master_id_col]: normalize_sex(row[master_sex_col])
        for _, row in master.iterrows()
    }
    out = survey_df.copy()
    out[out_col] = out[survey_id_col].map(sex_map)
    return out
