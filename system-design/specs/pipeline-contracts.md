# Orchestrator contracts spec

Strawmen for design review. This file specifies:

1. S3 path conventions (single source of truth — producer and consumer derive paths from the same inputs).
2. DB schema (six tables: `reach_network`, `desired_state`, `current_state`, `runs`, `overrides`, `metadata`) and the `desired_state_log` concept.
3. Manifest schemas (`override.manifest.yaml`, `model.manifest.json`, `run.json`).
4. Worker function signatures (`reach_build`, `plan_scenarios`, `reach_scenario_run`) and the state-store abstraction.

## Scope: orchestrator vs tooling

Architecture overview in [`orchestrator-design.md`](../orchestrator-design.md). This spec defines the contracts.

**Orchestrator owns:**
- Worker function signatures (what goes in / comes out / idempotency). Signatures are tooling-defined; orchestrator adapts.
- `plan_scenarios` (renamed from `reach_scenario_set`).
- State store, reconciliation loop, network propagator, trigger consolidation — see [`orchestrator-design.md`](../orchestrator-design.md).
- S3 path conventions, DB schema ownership.

**Tooling owns:**
- Manifest schemas (`override.manifest.yaml`, `model.manifest.json`, `run.json`).
- Hash rules.
- Supporting dataclasses for `reach_build` inputs.
- Internal implementation of `reach_build` and `reach_scenario_run` (opaque).
- Path-builder script (`s3_paths.py`).

Schemas and dataclasses below are kept for context until the tooling spec exists.

---

## 1. S3 path conventions

**Owner:** orchestrator (the conventions / layout). Path-builder script implementation: tooling (inferred).

All paths sit under a single root configurable via `STORE_ROOT` (real S3 bucket URI or local FS directory). Layout:

```
{STORE_ROOT}/version=v{MAJOR}/
├── overrides/reach={reach_id}/{override_name}/
│       ├── patch.tif
│       └── manifest.yaml
│
├── models/reach={reach_id}/{model_identity_hash}+{domain_geohash}/
│       ├── manifest.json
│       ├── metadata.csv / parquet
│       ├── {dem,roughness}.tif             # derived; deletable after N days
│       └── {centerline,inflow,outflow,domain,stl}.geojson
│
└── results/reach={reach_id}/{model_identity_hash}/{run_identity_hash}/
        └── z={z_label}/f={f_label}/
            ├── depth.tif             # COG, EPSG:5070; also hotstart seed
            ├── stl.geojson           # Stage Transfer Line
            ├── metadata.csv / parquet
            └── run.json              # PUT LAST — completion event
```

**Identity vs realization.** Model = model_identity (reach + methodology + overrides) + realization (domain). Run = run_identity (engine + engine version) + realization (scenario: z, f). Identity and realization are always separate in hashes and DB columns, so runs with the same model_identity stay valid even if the domain changes.

**Note:** `+` separator in model path TBD (literal character or notation).

**Conventions:**

| Symbol | Type | Format | Example |
|---|---|---|---|
| `{MAJOR}` | int | bare integer | `1` |
| `{reach_id}` | int | NHDPlus / NextGen reach ID | `12345` |
| `{override_name}` | str | `YYYY-MM-DD_kebab-slug` | `2026-05-01_levee-fix` |
| `{model_identity_hash}` | str | hash of model identity (reach + methodology + overrides) | `f4a9bc12d6e80f3a` |
| `{domain_geohash}` | str | hash of domain realization (bbox, resolution, CRS) | `a7c31e09` |
| `{run_identity_hash}` | str | hash of run identity (engine + engine version) | `1c8e44b9a2305f7d` |
| `{z_label}` | str | elevation (KWSE); `nd` for normal-depth baseline runs. Consistent with ripple1d. | `283`, `nd` |
| `{f_label}` | str | flow (Q) in cms. Consistent with ripple1d. | `200` |

**Path builder**: all S3 paths MUST be constructed via the path-builder script — never hand-format a path.

---

## 2. DB schema

**Owner:** orchestrator. Backend: SQLite in mock, Postgres in production.

### 2.1 `reach_network`

Static topology table loaded from hydrofabric data.

```sql
CREATE TABLE reach_network (
    reach_id      INTEGER PRIMARY KEY,
    reach_to_id   INTEGER REFERENCES reach_network(reach_id),  -- NULL for terminal reaches
    is_terminal   BOOLEAN NOT NULL DEFAULT FALSE,
    is_headwater  BOOLEAN NOT NULL DEFAULT FALSE,
    is_lake       BOOLEAN NOT NULL DEFAULT FALSE,
    geom          GEOMETRY
);
```

### 2.2 `desired_state`

Authored intent — what the system should produce. Nullable fields mean "use default source"; a value means it is authored. `revision` bumps on every change.

```sql
CREATE TABLE desired_state (
    reach_id                              INTEGER PRIMARY KEY REFERENCES reach_network(reach_id),
    min_flow                              REAL,        -- nullable: NULL = use default
    max_flow                              REAL,
    initial_dq_step_for_nd                REAL,
    solver                                TEXT,
    model_domain                          GEOMETRY,    -- bbox of the model domain
    override_id                           TEXT REFERENCES overrides(override_id),
    sdr_commit                            TEXT,
    library_density_mean_stage_threshold  REAL,
    library_density_max_stage_threshold   REAL,
    library_density_max_stage_interval    REAL,
    q_set                                 TEXT,        -- JSON array of flow values [100, 200, ...]
    ds_min_kwse                           REAL,
    ds_max_kwse                           REAL,
    revision                              INTEGER NOT NULL DEFAULT 0,
    updated_at                            TIMESTAMP,   -- added: mock audit trail (production uses desired_state_log)
    updated_by                            TEXT          -- added: mock audit trail
);
```

`updated_at`/`updated_by` for audit (see §2.7).

### 2.3 `current_state`

What the system has actually achieved. Part derived cache (from runs), part orchestrator state (`processing`). All columns NOT NULL — holds effective values. Reconciliation check: reaches in `desired_state` that have no `current_state` row (cold start) or `applied_revision < revision`.

`model_hash` = `{model_identity_hash}+{domain_geohash}` — the same string used as the S3 folder name under `models/reach={reach_id}/`. Given a `model_hash`, we can construct the S3 path directly.

```sql
CREATE TABLE current_state (
    reach_id            INTEGER PRIMARY KEY REFERENCES reach_network(reach_id),
    model_hash          TEXT NOT NULL,
    model_identity_hash TEXT NOT NULL,
    domain_hash         TEXT NOT NULL,
    processing          BOOLEAN NOT NULL DEFAULT FALSE,
    q_set               TEXT NOT NULL,     -- JSON array of completed Q values
    ds_min_kwse         REAL NOT NULL,
    ds_max_kwse         REAL NOT NULL,
    applied_revision    INTEGER NOT NULL DEFAULT 0
);
```

How `current_state` is formed: orchestrator gets job completion signal, verifies S3 artifact exists, then updates DB.

### 2.4 `runs` (ledger)

Append-only ledger of every run. `transfer_bc_from_*` columns are critical for propagation discovery (mechanism b in the network propagator).

Note: `run_identity_hash` hashes run identity only (engine + engine version), per the guide's identity/realization separation. The scenario realization (q, kwse) is NOT part of the hash — it lives in the S3 path as a subfolder (`z={z}/f={f}`) and in the `q_cms`/`kwse_m` columns. The PK therefore includes `model_identity_hash` and scenario columns to ensure uniqueness across different models and scenarios sharing the same engine.

```sql
CREATE TABLE runs (
    reach_id                  INTEGER NOT NULL REFERENCES reach_network(reach_id),
    run_identity_hash         TEXT NOT NULL,
    model_hash                TEXT NOT NULL,
    model_identity_hash       TEXT NOT NULL,    -- added: group runs by identity (guide: "runs with same model_identity stay valid")
    run_type                  TEXT NOT NULL CHECK (run_type IN ('nd', 'kwse')),  -- added: distinguish ND from KWSE runs
    q_cms                     REAL NOT NULL,
    bc_type                   TEXT NOT NULL,
    kwse_m                    REAL,
    depth_uri                 TEXT NOT NULL,
    stl_nominal_wse           REAL,
    status                    TEXT NOT NULL CHECK (status IN ('completed', 'failed', 'cancelled')),  -- added: record failures/cancellations
    started_at                TIMESTAMP,       -- added: monitoring/SLA
    completed_at              TIMESTAMP,       -- added: monitoring/SLA
    hotstart_from_run_hash    TEXT,             -- added: hotstart chain provenance
    transfer_bc_from_reach_id INTEGER,         -- added: propagation discovery (triggers spec §3.1 mechanism b)
    transfer_bc_from_run_hash TEXT,             -- added: propagation discovery (triggers spec §3.1 mechanism b)
    -- PK includes model + scenario columns because run_identity_hash is engine-only (not scenario-unique)
    PRIMARY KEY (reach_id, model_identity_hash, run_identity_hash, q_cms, kwse_m)
);
```

### 2.5 `overrides`

User-authored patches applied to reach models. A reach can have multiple overrides; `desired_state.override_id` references a single override.

```sql
CREATE TABLE overrides (
    override_id TEXT PRIMARY KEY,
    reach_id    INTEGER NOT NULL REFERENCES reach_network(reach_id),
    created_at  TIMESTAMP NOT NULL,
    created_by  TEXT NOT NULL,
    description TEXT
);
```

### 2.6 `metadata`

Placeholder table(s) — `reach_id` PK. Schema TBD.

### 2.7 `desired_state_log` (proposed — production only)

Append-only audit log for `desired_state` changes. Not implemented in the mock — mock uses `updated_at`/`updated_by` on `desired_state` directly.

```sql
CREATE TABLE desired_state_log (
    id           SERIAL PRIMARY KEY,
    reach_id     INTEGER NOT NULL REFERENCES reach_network(reach_id),
    revision     INTEGER NOT NULL,          -- the revision this change produced
    changed_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    changed_by   TEXT NOT NULL,             -- 'system' | 'operator' | user identifier
    change_type  TEXT NOT NULL CHECK (change_type IN ('created', 'updated', 'reverted')),
    old_values   JSONB,                     -- snapshot of changed fields before
    new_values   JSONB                      -- snapshot of changed fields after
);
CREATE INDEX idx_dsl_reach ON desired_state_log(reach_id, revision);
```

---

## 3. Schemas

**Owner:** tooling. The orchestrator only *consumes* these — it does not define or evolve the field set. Schemas below are kept in this spec for context until the tooling spec exists.

**Status (2026-05-14):** tooling team confirmed in the Dewberry-call meeting that they will start on schemas soon. Once their spec lands, the schemas below move out of this file and become a pointer.

### 3.1 `override.manifest.yaml`

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

### 3.2 `model.manifest.json`

Lives at `models/reach={reach_id}/{model_identity_hash}+{domain_geohash}/manifest.json`. **Content-addressed:** the path encodes both identity and realization hashes.

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
    "model_manifest_uri": "models/reach=12345/{model_identity_hash}+{domain_geohash}/manifest.json",
    "rasters": {
      "dem": "models/reach=12345/{model_identity_hash}+{domain_geohash}/dem.tif",
      "roughness": "models/reach=12345/{model_identity_hash}+{domain_geohash}/roughness.tif"
    },
    "vectors": {
      "centerline": "models/reach=12345/{model_identity_hash}+{domain_geohash}/centerline.geojson",
      "inflow": "models/reach=12345/{model_identity_hash}+{domain_geohash}/inflow.geojson",
      "outflow": "models/reach=12345/{model_identity_hash}+{domain_geohash}/outflow.geojson",
      "domain": "models/reach=12345/{model_identity_hash}+{domain_geohash}/domain.geojson",
      "stl": "models/reach=12345/{model_identity_hash}+{domain_geohash}/stl.geojson"
    }
  },

  "created_at": "2026-05-12T18:00:00Z",
  "built_by": "reach_build@v0.1"
}
```

**Hash rule.** `model_identity_hash` is sha256 over **canonicalized** JSON. When computing the hash, `domain.*`, `outputs.*`, `created_at`, and `built_by` are **excluded** (domain is realization, not identity).

### 3.3 `run.json`

Lives at `results/reach={reach_id}/{model_identity_hash}/{run_identity_hash}/z={z}/f={f}/run.json` **PUT LAST.** Content-addressed by `run_identity_hash`.

```json
{
  "schema_version": 1,
  "reach_id": 12345,
  "model_identity_hash": "f4a9bc12d6e80f3a",
  "model_hash": "f4a9bc12d6e80f3a+a7c31e09",
  "run_identity_hash": "1c8e44b9a2305f7d",

  "run_type": "kwse",                          // "nd" | "kwse"
  "scenario": {
    "z_label": "283",
    "f_label": "200",
    "q_value_cms": 200.0,
    "kwse_value_ft": 2.5
  },

  "boundary_conditions": [
    {"location": "us_bc_line", "kind": "QFIX", "value": 200.0, "units": "cms"},
    {"location": "transfer_line", "kind": "HFIX", "value": 2.5, "units": "ft",
     "source": {
       "kind": "stage_transfer",
       "from_reach_id": 12346,
       "from_model_identity_hash": "ab0e91d7c4c52ee0",
       "from_run_identity_hash": "7f3d29ae0b15ddc1",
       "sampled_from": "results/reach=12346/.../z=283/f=200/depth.tif"
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
    "hotstart_from": "results/reach=12345/.../z=283/f=200/depth.tif"
  },

  "outputs": {
    "depth_tif": "results/reach=12345/{model_identity_hash}/{run_identity_hash}/z=283/f=200/depth.tif",
    "stl_geojson": "results/reach=12345/{model_identity_hash}/{run_identity_hash}/z=283/f=200/stl.geojson"
  },

  "created_at": "2026-05-12T18:08:44Z"
}
```

Hash rule mirrors `model.manifest.json`: exclude `outputs`, `execution`, `created_at` from the hashed canonical form. Inputs include `model_identity_hash`, `run_type`, `scenario`, `boundary_conditions`, `solver` (image digest etc.).

---

## 4. Worker function signatures

**Contract:** signatures are tooling-defined; the orchestrator adapts when they change.

Workers are **stateless functions**: `(inputs) → S3 artifacts`.

**State is in the DB + S3, not in returns.** Workers may return a thin advisory result (e.g., `completed` vs `reused`) as a hint to avoid redundant S3 reads, but the orchestrator MUST be able to reconstruct full workflow state from `current_state` + S3 artifacts — return values are not load-bearing. This makes workers safe to retry, replay, and resume after orchestrator crashes.

**Storage abstraction (`store`):** workers receive a `store` handle that abstracts S3 (or local FS in mock) reads/writes/lists. The handle's implementation lives in the tooling repo for `reach_build` and `reach_scenario_run`; in orchestrator code for `plan_scenarios`.

### 4.1 `reach_build`

**Contract:** signature tooling-defined, orchestrator adapts; implementation = tooling (opaque).

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
    If the computed model_identity_hash already exists in storage, no-op and return existing path.

    Side effects: writes to {store}/version=vN/models/reach={reach_id}/{model_identity_hash}+{domain_geohash}/
    Result: {reach_id, model_identity_hash, model_manifest_uri, status: "built" | "reused"}
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
    name: str  # uri derived via s3_paths.override_dir(reach_id, name)

@dataclass(frozen=True)
class DomainSpec:
    resolution_m: int
    bbox_5070: tuple[float, float, float, float]
    crs: str = "EPSG:5070"

@dataclass(frozen=True)
class ReachBuildResult:
    reach_id: int
    model_identity_hash: str
    model_manifest_uri: str
    status: Literal["built", "reused"]
```

### 4.2 `plan_scenarios`

**Owner:** orchestrator (signature + implementation). Renamed from `reach_scenario_set`.

```python
def plan_scenarios(
    reach_id: int,
    model_identity_hash: str,
    *,
    aep_targets: list[str],     # e.g. ["Q100", "Q500"]
    kwse_strategy: KwseStrategy,
    store: Store,
) -> ScenarioSet:
    """
    Plan the KWSE sweep for this reach given ND run outputs.

    Stateless: the worker discovers prior ND results by listing S3 under
    results/reach={reach_id}/{model_identity_hash}/.../z=nd/
    rather than receiving pre-computed URIs as a parameter.

    No persisted side effects. The ScenarioSet is returned in-memory to
    the orchestrator and is NOT written to S3. Scenarios are implicit —
    a pure function of (aep_targets, ds_kwse from listed ND runs,
    kwse_strategy) and can be recomputed at any time.

    Result: ScenarioSet(reach_id, model_identity_hash, scenario_set_hash,
    orders: list[ScenarioOrder]).
    """
```

**Mock simplification:** scenarios are "a function of (min_flow, max_flow, ds_kwse, system_configs)." In production, `ds_kwse` (the downstream known water surface elevation from ND results) may inform the KWSE sweep range. In the mock, the sweep range comes entirely from the static `kwse_strategy` config; ND results are used only to discover which flow values exist, not to derive sweep parameters.

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
    z_label: str
    f_label: str
    q_value_cms: float
    kwse_value_ft: float
    hotstart_uri: str | None  # path to prior scenario's depth.tif

@dataclass(frozen=True)
class ScenarioSet:
    reach_id: int
    model_identity_hash: str
    scenario_set_hash: str
    orders: list[ScenarioOrder]
```

### 4.3 `reach_scenario_run`

**Contract:** signature tooling-defined, orchestrator adapts; implementation = tooling (opaque).

On completion, the orchestrator reads `run.json`, records the run in the `runs` ledger, and updates `current_state`.

```python
def reach_scenario_run(
    reach_id: int,
    model_identity_hash: str,
    run_type: Literal["nd", "kwse"],
    z_label: str,
    f_label: str,
    q_value_cms: float,
    kwse_value_ft: float,
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
      2. stl.geojson
      3. metadata.csv / parquet
      4. run.json LAST. This is the completion event.

    Idempotent: if run_identity_hash exists at the expected path with run.json present, no-op and return existing path with status "reused".
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
    model_identity_hash: str
    run_identity_hash: str
    run_json_uri: str
    status: Literal["completed", "reused"]
    converged: bool
```

### 4.4 State store (DB access layer)

**Owner:** orchestrator (signature + implementation). Replaces the indexer from the prior architecture.

The state store is the module the orchestrator calls to read/write all DB tables.

```python
class StateStore:
    """
    DB access layer. The orchestrator is the sole consumer.
    Workers are stateless and never import or call this module.
    """

    def get_desired(self, reach_id: int) -> DesiredState: ...
    def get_current(self, reach_id: int) -> CurrentState: ...
    def compute_gap(self, reach_id: int) -> Gap: ...
    def update_current(self, reach_id: int, state: CurrentState) -> None: ...
    def record_run(self, run: RunRecord) -> None: ...
    def bump_revision(self, reach_id: int) -> int: ...
    def get_topology(self) -> list[ReachEdge]: ...
    def get_runs_for_reach(self, reach_id: int) -> list[RunRecord]: ...
```
