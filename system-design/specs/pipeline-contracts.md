# Pipeline contracts spec

Strawmen for design review. This file specifies:

1. S3 path conventions (single source of truth — producer and consumer derive paths from the same inputs).
2. Manifest schemas (`override.manifest.yaml`, `model.manifest.json`, `run.manifest.json`).
3. Interface types (`Store`, `Catalog`, `CatalogPolicy`).
4. Worker function signatures (`reach_build`, `reach_scenario_set`, `reach_scenario_run`, `indexer`).

## What feedback I'm seeking

1. **Field set in each manifest** — anything missing, anything noise?
2. **Hash exclusion rule** — exclude `outputs.*` + `created_at` + `built_by` from manifest hashes (so they don't self-reference)?
3. **Override semantics** — is folder = "one self-contained patch package (`patch.tif` + `manifest.yaml`)" the right unit?
4. **TRANSFER BC source pointer** — keep the verbose lineage (`from_reach_id` + `from_model_manifest_hash` + `from_run_hash` + `sampled_from`) so each run is self-describing, or trim?
5. **`scenarios.json` persistence** — write planner output to S3 for audit (currently marked optional in §4.2), or keep the plan implicit and reconstructable from `run.manifest.json` files?

---

## 1. S3 path conventions

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
│       ├── vectors/
│       │   ├── divide.geojson
│       │   ├── centerline.geojson
│       │   ├── us_bc_line.geojson
│       │   └── transfer_line.geojson
│       └── scenarios/                       # optional — planner snapshot for traceability
│           └── {scenario_set_hash}.json     # see §4.2
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
| `{q_label}` | str | `Q{annual_recurrence_interval}` | `Q100` |
| `{kwse_label}` | str | decimal with one fractional digit | `2.5` |

**Path builder**: s3 paths are constructed via python script. Producers and consumers MUST use it — never hand-format a path.

---

## 2. Schemas

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
    "q_value_cfs": 12300.0,
    "kwse_label": "2.5",
    "kwse_value_ft": 2.5
  },

  "boundary_conditions": [
    {"location": "us_bc_line", "kind": "QFIX", "value": 12300.0, "units": "cfs"},
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

## 3. Interface types

The worker functions in §4 reference three small adapter types that abstract "where data lives." Same worker code runs against any backend implementing these interfaces — local FS in the mock, real S3 / Postgres in production.

**`Store`** — read/write/exists/list against the artifact backend.

**`Catalog`** — upsert/query against the catalog backend.

**`CatalogPolicy`** + **`RetentionRules`** — declarative config loaded from `catalog_policy.yaml` at indexer startup. Tells the indexer which S3 keys to react to and how to map JSONPath expressions into catalog columns. (`CatalogSourceRule` is defined alongside the indexer in §4.4.)

---

## 4. Worker function signatures

Workers are **stateless functions** with the same shape: `(context, inputs) → outputs + side-effects-to-S3`. Return values are small JSON-serializable summaries used by the orchestrator. The three reach workers (`reach_build`, `reach_scenario_set`, `reach_scenario_run`) never touch the DB; only the `indexer` writes to the catalog.

### 4.1 `reach_build`

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

### 4.2 `reach_scenario_set`

```python
def reach_scenario_set(
    reach_id: int,
    model_manifest_hash: str,
    *,
    nd_run_uris: list[str],    # the ND run.manifest.json paths from prior step
    aep_targets: list[str],     # e.g. ["Q100", "Q500"]
    kwse_strategy: KwseStrategy,
    store: Store,
) -> ScenarioSet:
    """
    Plan the KWSE sweep for this reach given ND run outputs.

    Pure-ish: reads ND results + AEP target values and emits an ordered
    list of run orders. Inputs to the function are NOT ScenarioOrder
    objects — those are the *output* shape, produced internally from
    `aep_targets` and `kwse_strategy`.

    Side effects: optional — may write a scenarios.json snapshot at
    models/reach=<id>/<manifest_hash>/scenarios/<scenario_set_hash>.json
    for traceability. See §1 storage layout.

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
    q_value_cfs: float
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

### 4.3 `reach_scenario_run`

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

### 4.4 `indexer`

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
