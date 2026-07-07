#!/usr/bin/env python
"""Rebuild codebook/condition_concepts.csv from the public OMOP/OHDSI vocabulary.

Off-platform replacement for the AoU 2.0 Concept Set builder (see docs/concept-set-rebuild-plan.md):
the standard-concept descendants of each phenotype root are the same OMOP vocabulary the AoU CDR
uses, so we resolve them against the public OHDSI WebAPI (ATLAS demo) instead of waiting on the
workspace's CDR. For each phenotype we take the root standard concept(s), resolve all descendants,
keep the valid STANDARD Condition concepts, and write one row per concept with the descendants
enumerated (so phenotypes.py exact-match logic is complete without runtime expansion).

Run (stdlib only, needs network): python analysis/rebuild_concept_sets.py
Then: python tests/test_phenotypes.py
"""

from __future__ import annotations

import csv
import json
import urllib.request
from pathlib import Path

SOURCE = "ATLASPROD"
BASE = f"https://atlas-demo.ohdsi.org/WebAPI/vocabulary/{SOURCE}"
OUT = Path(__file__).resolve().parents[1] / "codebook" / "condition_concepts.csv"

# Root standard concepts per phenotype (docs/concept-set-rebuild-plan.md; rectum resolved to 443390).
ROOTS = {
    "asthma": [317009],
    "hypertension": [316866],
    "atrial_fibrillation": [313217],
    "colorectal_cancer": [4180790, 443390],  # Malignant tumor of colon + of rectum
    "prostate_cancer": [4163261],
    "breast_cancer": [4112853],
}


def _post(path: str, body) -> list:
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def resolve_descendants(root_ids: list[int]) -> list[int]:
    items = [
        {"concept": {"CONCEPT_ID": cid}, "isExcluded": False, "includeDescendants": True, "includeMapped": False}
        for cid in root_ids
    ]
    return _post("/resolveConceptSetExpression", {"items": items})


def lookup(ids: list[int]) -> list[dict]:
    out: list[dict] = []
    for i in range(0, len(ids), 500):
        out += _post("/lookup/identifiers", ids[i : i + 500])
    return out


def main():
    rows = []
    for pheno, roots in ROOTS.items():
        ids = resolve_descendants(roots)
        details = lookup(ids)
        kept = [
            c for c in details
            if c["STANDARD_CONCEPT"] == "S" and c["DOMAIN_ID"] == "Condition" and c["INVALID_REASON"] == "V"
        ]
        kept.sort(key=lambda c: c["CONCEPT_NAME"])
        note = f"OHDSI descendant rebuild (root {'+'.join(map(str, roots))})"
        for c in kept:
            rows.append({
                "concept_id": c["CONCEPT_ID"], "concept_name": c["CONCEPT_NAME"],
                "vocabulary": c["VOCABULARY_ID"], "disease_group": pheno,
                "include_descendants": "no", "notes": note,
            })
        sample = ", ".join(c["CONCEPT_NAME"] for c in kept[:3])
        print(f"{pheno:20s}: {len(kept):3d} standard Condition concepts (of {len(ids)} resolved) | e.g. {sample}")

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["concept_id", "concept_name", "vocabulary", "disease_group", "include_descendants", "notes"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
