# Post-Migration Validation (RW 2.0)

*Started 2026-06-30. Records the actual results of runbook Step 4 (`docs/migration-aou-2.0.md`).*

## Status
- Migration to Researcher Workbench 2.0 (Verily): **files confirmed present.**
- Analysis compute: **BLOCKED** by a Verily-side IAM bug (see Blocker).
- Config-value capture: **partial** (compute-dependent values pending; CLI workaround in flight).

## Confirmed (Task 1 - file presence)
- Migrated workspace opened in RW 2.0; same title "Hillsborough Statistical Genetics Legacy Project".
- Migration bucket: `gs://rw-migration-aou-rw-1fda26b2` (region us-central1).
- Notebooks under `notebooks/`: `HLP_Project.ipynb` (134.6 KB) and `new5.ipynb` (1.9 KB).
  - Note capitalization: cloud is `HLP_Project.ipynb`; our repo copy is `aou/HLP_project.ipynb`.
  - Cloud notebook (134.6 KB) is larger than our Jun-20 base (~95 KB) - expect added code and/or
    embedded outputs. `new5.ipynb` is an unexplained small scratch notebook - inspect during reconcile.
- `merged_df/` absent - expected (we chose to re-run fresh, not rescue the stale persistent disk).

## Captured config values
| Var | Value | Source |
|-----|-------|--------|
| WORKSPACE_NAMESPACE | `aou-rw-1fda26b2` | UI (unchanged from legacy) |
| GOOGLE_PROJECT | `wb-halcyon-aubergine-9874` | UI (new 2.0 project) |
| CDR version | `C2024Q3R9` (cdrv8 - R9, version-bound) | UI (referenced BQ dataset) |
| WORKSPACE_CDR | `wb-silky-artichoke-2408.C2024Q3R9` | `wb resource list` (BQ_DATASET, REFERENCED, 118 tables, us-central1) |
| CDR_STORAGE_PATH | (v8, likely `gs://fc-aou-datasets-controlled/v8`) | confirm against notebook; CDR release unchanged from legacy |
| WORKSPACE_BUCKET | `gs://rw-migration-aou-rw-1fda26b2` | `wb resource list` (GCS_BUCKET, CONTROLLED migration bucket) |

**Key finding:** the 2.0 CDR is still `C2024Q3R9` (v8, R9) - the SAME release as legacy. Only the
BQ project prefix changed (`wb-silky-artichoke-2408` vs the legacy `fc-aou-cdr-prod-ct`). So the
v7/v8 concern in runbook Step 4 is moot; notebook path fixes reduce to swapping the project prefix,
not a CDR-version migration. Confirm the genomic `wgs/` / `CDR_STORAGE_PATH` against the notebook.

CLI installed and authenticated (`wb` 0.422.465, JAVA_HOME=/opt/homebrew/opt/openjdk@17,
`cclinton@researchallofus.org`, role OWNER). Extraction proceeding via `wb gsutil` / `wb bq`.

These three pending values gate the notebook path fixes (runbook Step 4 / roadmap M1->M3).

## Blocker: Carter's pet service account not provisioned (per-user, NOT workspace-wide)
**2026-07-02 update:** Jalen (owner `jfrank@`, the Creator who ran the migration) **can launch a
Jupyter environment** and work inside the perimeter normally. So the workspace itself is fine; the
gap is specific to **Carter's (`cclinton@`) identity** on the migrated workspace: his pet/workspace
service account was never provisioned (`wb auth status` -> "Service account email for current
workspace: (undefined)"), even though `wb workspace describe` shows him as Highest Role: OWNER.
The migration wired up the Creator but not the co-owner.

**Immediate unblock:** route the in-cloud extraction (concept-set queries, notebook pull, config
capture) to Jalen, whose environment works. The Verily ticket is no longer the critical path; it is
now just about getting Carter his own working environment.

For Carter's identity, the missing pet SA causes three cascading failures (all resolved for Jalen):

1. **Compute won't launch.** Creating a Jupyter app fails reproducibly with status Error:
   > Required 'compute.instances.getGuestAttributes' permission for
   > 'projects/wb-halcyon-aubergine-9874/zones/us-central1-a/instances/aoujupytercomputeengine20260630'
2. **Controlled bucket denies access.** `wb gsutil ls gs://rw-migration-aou-rw-1fda26b2` ->
   `403 storage.objects.list denied` (falls back to user identity `cclinton@`, which lacks direct
   bucket IAM because the pet SA that should hold it does not exist).
3. **CDR BigQuery blocked.** `wb bq query` against `wb-silky-artichoke-2408.C2024Q3R9` ->
   `VPC Service Controls: Request is prohibited by organization's policy`.

**Action: Verily support ticket** (see ticket text below / in chat). Project
`wb-halcyon-aubergine-9874`, namespace `aou-rw-1fda26b2`, missing pet service account.

## Why the CLI cannot substitute for the data plane
The CLI works for the **control plane** (auth, `workspace describe`, `resource list/resolve`) - that
is how the config values above were captured. But the **data plane** is sealed:
- All of Us controlled-tier data (CDR + controlled buckets) lives inside a **VPC Service Controls
  perimeter**. `bq` / `gsutil` from a laptop are outside the perimeter, so org policy blocks them
  BY DESIGN. Not a bug, not fixable client-side.
- Bucket access additionally needs the workspace pet SA, which is unprovisioned.

Therefore the notebook pull (#3/#4) and the concept-set queries (#2) both REQUIRE the in-perimeter
analysis environment. They are blocked by the same provisioning gap as compute, not independent of
it. Once Verily provisions the pet SA and compute launches, run the concept queries IN A NOTEBOOK
(Python BigQuery client, as originally planned) and pull the notebook via the Resources tab /
in-env `gsutil`. CLI docs: https://support.workbench.verily.com/docs/guides/cli/cli_install_and_run/

## Verily support ticket (send this)
> Subject: Co-owner has no pet service account on a migrated RW 2.0 workspace (owner works fine)
>
> Workspace namespace: `aou-rw-1fda26b2` ("Hillsborough Statistical Genetics Legacy Project"),
> migrated ~2026-06-25, project `wb-halcyon-aubergine-9874`, CDR `C2024Q3R9` (v8).
>
> The workspace Owner/Creator (`jfrank@researchallofus.org`) can launch a Jupyter environment and
> work normally, so the workspace is provisioned correctly. The co-owner
> (`cclinton@researchallofus.org`, shown as Highest Role: OWNER) cannot: his workspace pet/service
> account was never provisioned (`wb auth status` -> "Service account email for current workspace:
> (undefined)"). For cclinton@ this cascades to:
> 1. Jupyter app launch fails: `Required 'compute.instances.getGuestAttributes' permission for
>    'projects/wb-halcyon-aubergine-9874/zones/us-central1-a/instances/aoujupytercomputeengine20260630'`
> 2. Controlled bucket: `wb gsutil ls gs://rw-migration-aou-rw-1fda26b2` -> 403 storage.objects.list
>    denied for cclinton@.
> (CDR BigQuery over the CLI is separately VPC-SC blocked from outside the perimeter; that is
> expected and not part of this request.)
>
> Request: provision the workspace pet service account for cclinton@ on this migrated workspace and
> grant the required compute + bucket IAM, so his analysis environments launch. The migration
> appears to have provisioned the Creator but not the co-owner.

## Notebook path-fix scope (#3) - ready to apply post-reconciliation
Read-only grep of `aou/HLP_project.ipynb` (Jun-20 base):
- `os.environ["WORKSPACE_CDR"]` x101, plus `WORKSPACE_BUCKET` / `GOOGLE_PROJECT` via os.environ ->
  dynamic, need NO change (resolve correctly in 2.0).
- Genomic paths use the shared `gs://fc-aou-datasets-controlled/...` bucket (same for all v8
  workspaces) -> unchanged by migration.
- **Only real fix:** one hardcoded `fc-aou-datasets-controlled/v7/wgs/` should be `v8/wgs/`
  (all other genomic paths are already v8; workspace CDR is v8). One-character change.
- Reconcile against Jalen's Jun-21 cloud `HLP_Project.ipynb` first (it may differ), then apply.
