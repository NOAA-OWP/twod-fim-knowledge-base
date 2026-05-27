# Orchestrator Design

Detailed schemas, paths, and worker signatures in [`specs/pipeline-contracts.md`](specs/pipeline-contracts.md) and [`specs/triggers-and-propagation.md`](specs/triggers-and-propagation.md).

## System Shape

Postgres is the brain, Dagster is the controller, workers are stateless, S3 is the artifact plane.

```mermaid
flowchart LR
    Actor["operator / system update"] --> O
    subgraph DB["Postgres"]
        DS["desired_state"]
        CS["current_state"]
        RN["reach_network"]
        R["runs"]
        OV["overrides"]
    end
    O["Dagster orchestrator<br/>reconciliation loop"]
    subgraph W["stateless workers"]
        Build["reach_build"]
        Scenarios["plan_scenarios"]
        Run["reach_scenario_run"]
    end
    subgraph S3["S3"]
        Models["models/"]
        Results["results/"]
    end
    DB <--> O
    O --> W
    Build --> Models
    Run --> Results
```

| Rule | Detail |
|---|---|
| State advances only after S3 verification | Orchestrator gets completion signal, checks S3, then writes DB |
| Completion signal | `manifest.json` (model build) or `run.json` (scenario run) PUT LAST at expected S3 path |

### DB tables

| Table | Purpose |
|---|---|
| `desired_state` | What the system should produce per reach. `revision` increments on change. Nullable fields = use default. |
| `current_state` | What's been achieved. `applied_revision` tracks last applied. Gap = `applied_revision < revision`. |
| `runs` | Per-run ledger with BC provenance for propagation. |
| `reach_network` | Topology — reach_id, reach_to_id, terminal/headwater/lake flags. |
| `overrides` | User-authored patches. `override_id` (PK), `reach_id` (FK). `desired_state` references a single override. |
| `desired_state_log` | Append-only audit log — who changed what, when, and why. |
| `metadata` | TBD. |

Full DDL in [pipeline-contracts.md §2](specs/pipeline-contracts.md).

## S3 Paths — Identity vs Realization

Identity and realization are always separate in hashes and paths.

```
models/reach={id}/{model_identity_hash}+{domain_geohash}/
    manifest.json, dem.tif, roughness.tif, vectors...

results/reach={id}/{model_identity_hash}/{run_identity_hash}/z={z}/f={f}/
    depth.tif, stl.geojson, run.json
```

- **model_identity_hash** = reach + methodology + overrides (domain excluded)
- **domain_geohash** = spatial realization (bbox, resolution)
- **run_identity_hash** = engine + engine version
- **z** = elevation (KWSE), **f** = flow (Q) — consistent with ripple1d
- Results filed under model_identity only — runs survive domain changes

## Reach Processing (cold start)

```mermaid
flowchart TD
    Gap["gap detected for reach R"] --> Build["reach_build"]
    Build --> UpBuild["verify S3 → update current_state<br/>(model exists, model_hash)"]
    UpBuild --> ND["reach_scenario_run × N<br/>ND runs"]
    ND --> UpND["verify S3 → update current_state<br/>(q_set, run records)"]
    UpND --> Plan["plan_scenarios<br/>KWSE sweep from ND results"]
    Plan --> KWSE["reach_scenario_run × M<br/>KWSE runs with hotstart chain"]
    KWSE --> UpKWSE["verify S3 → update current_state<br/>(min/max kwse, run records)"]
    UpKWSE --> Done["set applied_revision = revision"]
    Done --> Prop{"upstream reaches<br/>depend on R?"}
    Prop -- "yes" --> Bump["bump their revision"]
    Prop -- "no" --> Wait["done"]
```

## Reconciliation Loop

Each tick moves current state toward desired state. Content-addressed paths make the loop safe to retry.

```mermaid
flowchart TD
    Tick["sensor tick"] --> Gap{"no current_state row<br/>or applied_revision < revision?"}
    Gap -- "no" --> Wait["wait"]
    Gap -- "yes" --> Read["read desired + current"]
    Read --> Schedule["schedule reach processing<br/>(build → ND → plan → KWSE)"]
    Schedule --> Verify["workers write S3<br/>orchestrator verifies"]
    Verify --> Update["update current_state + runs"]
    Update --> Upstream{"upstream depends<br/>on changed output?"}
    Upstream -- "yes" --> Bump["bump upstream revision"]
    Upstream -- "no" --> Wait
    Bump --> Wait
```

## DB Listening

Polling is primary — simple, observable, guaranteed progress.

```mermaid
sequenceDiagram
    participant Orch as Dagster sensor
    participant DB as Postgres
    participant Worker as Worker
    participant S3 as S3
    loop fixed interval
        Orch->>DB: query revision gaps
        DB-->>Orch: reaches needing work
        Orch->>Worker: submit stateless job
        Worker->>S3: write artifacts + run.json last
        Orch->>S3: verify expected artifact
        Orch->>DB: update current_state and runs
    end
```

| Mechanism | Role |
|---|---|
| Polling | Primary. Finds `applied_revision < revision` gaps. |
| S3 verification | Required. Confirms artifact before DB advances. |
| Periodic S3 rescan | Safety net. Repairs DB/S3 drift. |
| LISTEN/NOTIFY | Optional. Wakes poller faster. |

## Dagster Fit

```mermaid
flowchart LR
    DS["desired_state.revision"] --> Sensor["sensor polls DB"]
    Sensor --> Assets["asset graph"]
    Assets --> Parts["partitions<br/>(reach_id, q, kwse)"]
    Parts --> Runs["Dagster runs"]
    Runs --> Fleet["workers<br/>(AWS Batch)"]
```

| Option | Fit | Why |
|---|---|---|
| **Dagster** | Strong | Asset materialization + partition state = desired vs current. Built-in sensors, run cancellation, backfills, UI. |
| Airflow | Weaker | DAG-run oriented. No native asset staleness or partition catalog. |
| Prefect | Weaker | Flexible flows but less opinionated on asset lineage and materialization tracking. |
| Custom | Possible | Closest pattern match but rebuilds scheduling, UI, retries, backfills from scratch. |
