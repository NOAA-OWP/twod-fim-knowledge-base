# Pipeline contracts spec

Strawmen for design review. This file specifies:

1. S3 path conventions (single source of truth — producer and consumer derive paths from the same inputs).
2. Manifest schemas (`override.manifest.yaml`, `model.manifest.json`, `run.manifest.json`).
3. Worker function signatures (`reach_build`, `reach_scenario_set`, `reach_scenario_run`, `indexer`).

## Scope: pipeline vs tooling

Per PR #73 review, the pipeline repo owns *orchestration and reaction*; the tooling repo owns *what artifacts are and how they get built*. Concretely:

**Pipeline owns:**
- Worker function *signatures* and orchestration contracts (what goes in / comes out / idempotency).
- `reach_scenario_set` as a pipeline function (first iteration — PR #73 comment #11: *"I think in first iteration, we can consider this a pipeline function. So this one does belong to pipeline."*).
- The indexer.
- Sensors (`override_added_sensor`, `run_manifest_landed_sensor`, etc.) — see [`triggers-and-invalidation.md`](triggers-and-invalidation.md).
- **Network propagator** — given a new `run.manifest.json` for reach R, discover upstream reaches whose runs depended on R's prior outputs and trigger their new partitions. Multi-hop. **Proposed design (TBD pending team review):** two complementary discovery mechanisms — *(a) topology graph walk* yields candidate upstream reaches with bounded fan-out; *(b) catalog lookup on `boundary_conditions[].source.from_run_hash`* confirms which candidates actually need re-running (vs. those already pointing at the new R hash or sampled from a different downstream version). Topology alone over-fires; catalog alone over-scans. See triggers spec for detailed algorithm (still being designed). *Pipeline requirement on the tooling schema: for mechanism (b), `run.manifest.json`'s TRANSFER BC source must carry upstream-discoverable pointers (e.g., `from_run_hash`) — coordinate with tooling on the minimum field set. Without them, propagation falls back to topology-only and over-fires.*
- **Trigger consolidator** — given multiple triggers arriving close in time (or while related work is in flight), decide whether to coalesce, queue, or kill in-flight. Algorithm TBD (see triggers spec).
- S3 path *conventions* at the contract level (so the pipeline knows where to watch).
- The catalog's currency semantics and how consumers query "current."

**Tooling owns (defined in the tooling repo, referenced here):**
- Manifest schemas — exact field set of `override.manifest.yaml`, `model.manifest.json`, `run.manifest.json` (PR #73 #1: *"this would be in the scope of our tooling repo"*; #6 and #7 on the schemas: *"This will be useful for when Scott would work towards creating this, I think this is beyond pipeline scope"*).
- Hash rules — what is excluded from the canonical-JSON hash (PR #73 #2: *"should be dealt with in the scope of other repo"*).
- Supporting dataclasses for `reach_build` inputs (`HydrofabricRef`, `DemSource`, `RoughnessSource`, `OverrideRef`, `DomainSpec`, etc.) (PR #73 #10: *"Beyond the scope of pipeline"*).
- Internal implementation of `reach_build` and `reach_scenario_run` — the pipeline treats these as opaque black boxes (PR #73 #9: *"the pipeline should consider these functions opaque"*).
- *Inferred (not directly addressed in PR):* the path-builder script (`s3_paths.py`) — same domain as the schemas.

Sections below that describe schema fields and dataclass shapes are kept for context but are slated to move to the tooling repo once that spec exists.

## What feedback I'm seeking

1. **Field set in each manifest** — *Moved to tooling repo (PR #73 #1).*
2. **Hash exclusion rule** — *Moved to tooling repo (PR #73 #2).*
3. **Override semantics** — concretely: an override is one folder containing exactly `patch.tif` + `manifest.yaml`, and each folder = one independent patch package. The pipeline treats the folder as the indivisible unit when it fires `override_added`. Is this understanding correct?
4. ~~**TRANSFER BC source pointer**~~ — *Moved to tooling repo (schema concern). Pipeline-side requirement noted in the Network propagator bullet above.*
5. ~~**`scenarios.json` persistence**~~ — *Decided: scenarios are implicit (PR #73 #4, #14).*

---

## 1. S3 path conventions

**Owner:** pipeline (the conventions / layout). Path-builder script implementation: tooling (inferred).

All paths sit under a single root configurable via `STORE_ROOT` (real S3 bucket URI or local FS directory). Layout:

```
{STORE_ROOT}/version=v{MAJOR}/
├── overrides/reach={reach_id}/{override_name}/
│       ├── patch.tif
│       └── manifest.yaml
│
├── models/reach={reach_id}/{manifest_hash}/
│       ├── manifest.json
│       ├── rasters/
│       │   ├── dem.tif         # 30-day TTL via lifecycle policy
│       │   └── roughness.tif
│       └── vectors/
│           ├── divide.geojson
│           ├── centerline.geojson
│           ├── us_bc_line.geojson
│           └── transfer_line.geojson
│
└── results/reach={reach_id}/{model_manifest_hash}/{run_hash}/
        └── q={q_label}/kwse={kwse_label}/
            ├── depth.tif          # also hotstart for next scenario
            └── run.manifest.json  # PUT LAST — completion event
```

**Conventions:**

| Symbol | Type | Format | Example |
|---|---|---|---|
| `{MAJOR}` | int | bare integer | `1` |
| `{reach_id}` | int | NHDPlus / NextGen reach ID | `12345` |
| `{override_name}` | str | `YYYY-MM-DD_kebab-slug` | `2026-05-01_levee-fix` |
| `{manifest_hash}` | str | first 16 hex chars of `sha256(canonical_json(manifest.json))` | `f4a9bc12d6e80f3a` |
| `{model_manifest_hash}` | str | same as `{manifest_hash}` of the model this run targets | `f4a9bc12d6e80f3a` |
| `{run_hash}` | str | first 16 hex chars of `sha256(canonical_json(run.manifest.json))` | `1c8e44b9a2305f7d` |
| `{q_label}` | str | Return-period label per `guide.md` example (e.g. `Q100` = 100-year recurrence interval). PR #73 #5 raised an alternate `q_{value_cms}` form ("for 200 cms `q_200` or `f_200`"); path convention follows `guide.md` until that change lands explicitly. | `Q100` |
| `{kwse_label}` | str | decimal with one fractional digit | `2.5` |

**Path builder**: s3 paths are constructed via python script. Producers and consumers MUST use it — never hand-format a path.

---

## 2. Schemas

**Owner:** tooling. Pipeline only *consumes* these — pipeline does not define or evolve the field set. Schemas below are kept in this spec for context until the tooling spec exists.

**Status (2026-05-14):** tooling team confirmed in the Dewberry-call meeting that they will start on schemas soon. Once their spec lands, the schemas below move out of this file and become a pointer.

### 2.1 `override.manifest.yaml`

Lives at `overrides/reach={reach_id}/{override_name}/manifest.yaml`.

```yaml
override_name: "2026-05-01_levee-fix"          # str, matches folder name
reach_id: 12345                                # int
created_at: "2026-05-01T14:32:00Z"             # ISO UTC
created_by: "engineer.name"                    # str, human-readable
description: "Adds levee crest correction along left bank"   # str, free-form
patch_kind: "dem"                              # enum: "dem" | "roughness" | "vector"
patch_uri: "patch.tif"                         # str, path relative to this manifest
applies_to_bbox: [-95.10, 30.50, -94.90, 30.70]   # [minx, miny, maxx, maxy] in EPSG:5070
```

### 2.2 `model.manifest.json`

Lives at `models/reach={reach_id}/{manifest_hash}/manifest.json`. **Content-addressed:** `manifest_hash = sha256(canonical_json(this file))`.

```json
{
  "schema_version": 1,
  "reach_id": 12345,

  "version": {
    "major": 1,
    "minor": 2,
    "sdr_commit": "abc1234567890def"
  },

  "inputs": {
    "hydrofabric": {
      "source": "NextGen",
      "snapshot": "v2.2-conus",
      "vpu": 1
    },
    "dem": {
      "source": "USGS_3DEP",
      "snapshot_date": "2026-04-01",
      "resolution_m": 10
    },
    "roughness": {
      "source": "MRLC_NLCD",
      "snapshot_date": "2026-04-01"
    },
    "overrides": [
      {"name": "2026-05-01_levee-fix", "uri": "overrides/reach=12345/2026-05-01_levee-fix/"}
    ]
  },

  "domain": {
    "resolution_m": 10,
    "bbox_5070": [-95.10, 30.50, -94.90, 30.70],
    "crs": "EPSG:5070"
  },

  "twodimfim_version": "0.3.1",

  "outputs": {
    "model_manifest_uri": "models/reach=12345/{manifest_hash}/manifest.json",
    "rasters": {
      "dem": "models/reach=12345/{manifest_hash}/rasters/dem.tif",
      "roughness": "models/reach=12345/{manifest_hash}/rasters/roughness.tif"
    },
    "vectors": {
      "divide": "models/reach=12345/{manifest_hash}/vectors/divide.geojson",
      "centerline": "models/reach=12345/{manifest_hash}/vectors/centerline.geojson",
      "us_bc_line": "models/reach=12345/{manifest_hash}/vectors/us_bc_line.geojson",
      "transfer_line": "models/reach=12345/{manifest_hash}/vectors/transfer_line.geojson"
    }
  },

  "created_at": "2026-05-12T18:00:00Z",
  "built_by": "reach_build@v0.1"
}
```

**Hash rule.** `manifest_hash` is sha256 over **canonicalized** JSON. When computing the hash, the `outputs.*` fields, `created_at`, and `built_by` are **excluded**.

### 2.3 `run.manifest.json`

Lives at `results/reach={reach_id}/{model_manifest_hash}/{run_hash}/q={q}/kwse={kwse}/run.manifest.json`. **PUT LAST.** Content-addressed by `run_hash`.

```json
{
  "schema_version": 1,
  "reach_id": 12345,
  "model_manifest_hash": "f4a9bc12d6e80f3a",
  "run_hash": "1c8e44b9a2305f7d",

  "run_type": "kwse",                          // "nd" | "kwse"
  "scenario": {
    "q_label": "Q100",
    "q_value_cms": 200.0,
    "kwse_label": "2.5",
    "kwse_value_ft": 2.5
  },

  "boundary_conditions": [
    {"location": "us_bc_line", "kind": "QFIX", "value": 200.0, "units": "cms"},
    {"location": "transfer_line", "kind": "HFIX", "value": 2.5, "units": "ft",
     "source": {
       "kind": "stage_transfer",
       "from_reach_id": 12346,
       "from_model_manifest_hash": "ab0e91d7c4c52ee0",
       "from_run_hash": "7f3d29ae0b15ddc1",
       "sampled_from": "results/reach=12346/.../q=Q100/kwse=2.5/depth.tif"
     }}
  ],

  "solver": {
    "engine": "LISFLOOD-FP",
    "solver_kind": "acceleration",
    "use_cuda": true,
    "image": "lisflood-fp:latest-gpu@sha256:...",
    "engine_version": "8.0"
  },

  "execution": {
    "started_at": "2026-05-12T18:05:11Z",
    "ended_at":   "2026-05-12T18:08:43Z",
    "wall_seconds": 212.3,
    "converged": true,
    "iterations": 6,
    "mass_balance_error": 0.0021,
    "hotstart_from": "results/reach=12345/.../q=Q100/kwse=2.4/depth.tif"
  },

  "outputs": {
    "depth_tif": "results/reach=12345/{model_manifest_hash}/{run_hash}/q=Q100/kwse=2.5/depth.tif"
  },

  "created_at": "2026-05-12T18:08:44Z"
}
```

Hash rule mirrors `model.manifest.json`: exclude `outputs`, `execution`, `created_at` from the hashed canonical form. Inputs include `model_manifest_hash`, `run_type`, `scenario`, `boundary_conditions`, `solver` (image digest etc.).

---

## 3. Worker function signatures

**Owner:** signatures = pipeline contract. Implementations split per function (see each subsection).

Workers are **stateless functions**: `(inputs) → side-effects-to-S3`. They take inputs, produce S3 artifacts, and that's it. The three reach workers (`reach_build`, `reach_scenario_set`, `reach_scenario_run`) never touch the DB; only the `indexer` writes to the catalog.

**State is in S3, not in returns.** Workers may return a thin advisory result (e.g., `completed` vs `reused`) as a hint to avoid redundant S3 reads, but the orchestrator MUST be able to reconstruct full workflow state from S3 + catalog alone — return values are not load-bearing. This makes workers safe to retry, replay, and resume after orchestrator crashes.

**Storage abstraction (`store`):** workers receive a `store` handle that abstracts S3 (or local FS in mock) reads/writes/lists. The handle's implementation lives in the tooling repo for `reach_build` and `reach_scenario_run`; in pipeline code for `reach_scenario_set` and `indexer`.

### 3.1 `reach_build`

**Owner:** signature = pipeline contract; implementation = tooling (opaque to pipeline per PR #73 #9).

```python
def reach_build(
    reach_id: int,
    *,
    major_version: int = 1,
    hydrofabric_ref: HydrofabricRef,
    dem_source: DemSource,
    roughness_source: RoughnessSource,
    overrides: list[OverrideRef],
    domain: DomainSpec,
    twodimfim_version: str,
    sdr_commit: str,
    store: Store,
) -> ReachBuildResult:
    """
    Build a per-reach model manifest + rasters + vectors. Idempotent.
    If the computed manifest_hash already exists in storage, no-op and return existing path.

    Side effects: writes to {store}/version=vN/models/reach={reach_id}/{manifest_hash}/
    Result: {reach_id, manifest_hash, model_manifest_uri, status: "built" | "reused"}
    """
```

Supporting dataclasses:

```python
@dataclass(frozen=True)
class HydrofabricRef:
    source: str  # "NextGen" | "NHDPlusHR" | ...
    snapshot: str
    vpu: int

@dataclass(frozen=True)
class DemSource:
    source: str  # "USGS_3DEP"
    snapshot_date: str  # "YYYY-MM-DD"
    resolution_m: int

@dataclass(frozen=True)
class RoughnessSource:
    source: str  # "MRLC_NLCD"
    snapshot_date: str

@dataclass(frozen=True)
class OverrideRef:
    name: str
    uri: str  # relative to STORE_ROOT

@dataclass(frozen=True)
class DomainSpec:
    resolution_m: int
    bbox_5070: tuple[float, float, float, float]
    crs: str = "EPSG:5070"

@dataclass(frozen=True)
class ReachBuildResult:
    reach_id: int
    manifest_hash: str
    model_manifest_uri: str
    status: Literal["built", "reused"]
```

### 3.2 `reach_scenario_set`

**Owner:** pipeline (signature + implementation), per PR #73 #11. Will likely refactor with Dewberry later (PR #73 #13, #15).

```python
def reach_scenario_set(
    reach_id: int,
    model_manifest_hash: str,
    *,
    aep_targets: list[str],     # e.g. ["Q100", "Q500"]
    kwse_strategy: KwseStrategy,
    store: Store,
) -> ScenarioSet:
    """
    Plan the KWSE sweep for this reach given ND run outputs.

    Stateless: the worker discovers prior ND results by listing S3 under
    results/reach={reach_id}/{model_manifest_hash}/.../q=*/kwse=ND/
    rather than receiving pre-computed URIs as a parameter
    (PR #73 #12 — "We want to be stateless, so I would suggest we just
    read paths from S3").

    No persisted side effects. The ScenarioSet is returned in-memory to
    the orchestrator and is NOT written to S3. Scenarios are implicit —
    a pure function of (aep_targets, ds_kwse from listed ND runs,
    kwse_strategy) and can be recomputed at any time
    (PR #73 #4, #14).

    Result: ScenarioSet(reach_id, model_manifest_hash, scenario_set_hash,
    orders: list[ScenarioOrder]).
    """
```

Supporting dataclasses:

```python
@dataclass(frozen=True)
class KwseStrategy:
    kind: Literal["uniform_sweep", "adaptive"]
    step_ft: float = 0.1
    min_ft: float = 0.0
    max_ft: float = 10.0

@dataclass(frozen=True)
class ScenarioOrder:
    q_label: str
    q_value_cms: float
    kwse_label: str
    kwse_value_ft: float
    hotstart_uri: str | None  # path to prior scenario's depth.tif

@dataclass(frozen=True)
class ScenarioSet:
    reach_id: int
    model_manifest_hash: str
    scenario_set_hash: str
    orders: list[ScenarioOrder]
```

### 3.3 `reach_scenario_run`

**Owner:** signature = pipeline contract; implementation = tooling (opaque to pipeline per PR #73 #9).

```python
def reach_scenario_run(
    reach_id: int,
    model_manifest_hash: str,
    run_type: Literal["nd", "kwse"],
    boundary_conditions: list[BoundaryCondition],
    solver: SolverSpec,
    hotstart_uri: str | None,
    *,
    store: Store,
) -> RunResult:
    """
    Execute a single scenario via the engine container. Stateless.

    Writes (in this order):
      1. depth.tif
      2. (other artifacts if any)
      3. run.manifest.json LAST. This is the completion event.

    Idempotent: if run_hash exists at the expected path with run.manifest.json present, no-op and return existing path with status "reused".
    """
```

Supporting dataclasses:

```python
@dataclass(frozen=True)
class BoundaryCondition:
    location: str
    kind: Literal["QFIX", "HFIX", "FREE", "TRANSFER"]
    value: float
    units: str
    source: dict | None = None  # for TRANSFER: pointer to upstream-DS run

@dataclass(frozen=True)
class SolverSpec:
    engine: str  # "LISFLOOD-FP"
    solver_kind: str  # "acceleration" | "diffusive" | "fv1" | "dg2"
    use_cuda: bool
    image: str  # "lisflood-fp:latest-gpu@sha256:..."
    engine_version: str

@dataclass(frozen=True)
class RunResult:
    reach_id: int
    model_manifest_hash: str
    run_hash: str
    run_manifest_uri: str
    status: Literal["completed", "reused"]
    converged: bool
```

### 3.4 `indexer`

**Owner:** pipeline (signature + implementation).

**Catalog abstraction (`catalog`):** the indexer takes a `catalog` handle abstracting the backend — SQLite in the mock, Postgres in production. The handle supports `upsert(table, row, keys)` and `query(sql, params)`; only the indexer writes, consumers (`flows2fim`, web viewer) query.

**`CatalogPolicy` and `RetentionRules`:** declarative config loaded from `catalog_policy.yaml` at indexer startup. Tells the indexer (a) which S3 keys to react to, (b) how to map JSONPath expressions from `run.manifest.json` fields into catalog columns, and (c) retention rules for derived data (e.g., `derived_data_days: 30` for `models/.../rasters/`).

```python
def indexer(
    run_manifest_uri: str,
    *,
    policy: CatalogPolicy,
    catalog: Catalog,
) -> IndexerResult:
    """
    Triggered by the appearance of a new run.manifest.json (S3 ObjectCreated in prod, filesystem event in mock).

    Reads the run.manifest.json, applies the policy's field mapping, upserts a row in the catalog.

    Sole writer to the catalog. Workers never call this.
    """
```

Supporting dataclasses:

```python
@dataclass(frozen=True)
class CatalogPolicy:
    """Loaded from catalog_policy.yaml at indexer startup."""
    sources: list[CatalogSourceRule]
    retention: RetentionRules

@dataclass(frozen=True)
class CatalogSourceRule:
    prefix_pattern: str  # glob: "version=v1/results/reach=*/<...>/run.manifest.json"
    on_event: Literal["ObjectCreated", "ObjectRemoved"]
    target_table: str
    field_mapping: dict[str, str]  # column name → JSONPath into run.manifest.json
    upsert_keys: list[str]

@dataclass(frozen=True)
class RetentionRules:
    derived_data_days: int = 30           # delete DEM/roughness rasters etc under models/.../rasters/ after N days

@dataclass(frozen=True)
class IndexerResult:
    run_manifest_uri: str
    table: str
    rows_upserted: int
    status: Literal["upserted", "skipped"]
```
