# Orchestrator Design

Detailed schemas, paths, and worker signatures in [`specs/pipeline-contracts.md`](specs/pipeline-contracts.md) and [`specs/triggers-and-propagation.md`](specs/triggers-and-propagation.md).

## Reach Processing (cold start)

```mermaid
flowchart TD
    Gap["gap detected for reach R"] --> Build["reach_build (tooling)"]
    Build --> UpBuild["verify S3 → update current_state<br/>(model exists, model_hash)"]
    UpBuild --> ND["run_nd_scenarios (tooling)<br/>orchestrator passes q range"]
    ND --> UpND["verify S3 → update current_state<br/>(q_set, run records)"]
    UpND --> Plan["plan_scenarios<br/>KWSE sweep from ND results"]
    Plan --> KWSE["run_kwse_scenarios (tooling)<br/>(with hotstart chain)"]
    KWSE --> UpKWSE["verify S3 → update current_state<br/>(min/max kwse, run records)"]
    UpKWSE --> Done["set applied_revision = revision"]
    Done --> Prop{"upstream reaches<br/>depend on R?"}
    Prop -- "yes" --> Cascade["walk network + check hashes<br/>process affected upstream directly"]
    Prop -- "no" --> Wait["done"]
    Cascade --> Wait
```

Upstream reaches are processed as part of the original trigger's scope — their `desired_state.revision` is not bumped. If the orchestrator crashes mid-cascade, periodic S3 rescan detects completed artifacts and syncs `current_state`.

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
    Update --> Wait
```

`desired_state.revision` only changes from external events (config change, manual request). The loop detects the gap and processes the reach, including any upstream cascade.

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
| Periodic S3 rescan | Safety net. Repairs DB/S3 drift and crash recovery during upstream cascade. |
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
