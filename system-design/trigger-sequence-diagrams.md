# Trigger sequence diagrams

Sequence diagram versions of the trigger flowcharts in [`triggers-and-propagation.md`](triggers-and-propagation.md) §1.3. These show which components are touched and in what order.

## A. Full chain (rows 2, 7)

Model invalidated — rebuild everything.

```mermaid
sequenceDiagram
    actor Op as Operator
    participant DB as DB
    participant Orch as Orchestrator
    participant BM as build_model
    participant S3 as S3
    participant ND as run_nd_scenarios
    participant PS as plan_scenarios
    participant KWSE as run_kwse_scenarios

    Op->>DB: update desired_state (override_id or hydrofabric) + bump revision

    Note over Orch: sensor tick
    Orch->>DB: query gap (applied_revision < revision)
    DB-->>Orch: reach R needs work
    Orch->>DB: set current_state.processing = TRUE

    Orch->>BM: submit job (reach R)
    BM->>S3: write model artifacts
    BM->>S3: write manifest.json
    BM-->>Orch: done
    Orch->>S3: verify manifest.json exists
    Orch->>DB: update current_state (model_hash, model_identity_hash, domain_hash)

    Orch->>ND: submit job (reach R, q range)
    ND->>S3: write depth.tif
    ND->>S3: write run.json (PUT LAST)
    ND-->>Orch: done
    Orch->>S3: verify run.json exists
    Orch->>DB: update current_state (q_set)
    Orch->>DB: record run in runs table

    Orch->>PS: plan KWSE sweep (in-process)
    PS->>S3: list ND results
    PS-->>Orch: ScenarioSet

    Orch->>KWSE: submit job (reach R, scenarios)
    KWSE->>S3: write depth.tif
    KWSE->>S3: write run.json (PUT LAST)
    KWSE-->>Orch: done
    Orch->>S3: verify run.json exists
    Orch->>DB: update current_state (ds_min_kwse, ds_max_kwse)
    Orch->>DB: record run in runs table
    Orch->>DB: set applied_revision = revision, processing = FALSE

    Orch->>DB: query reach_network (upstream of R)
    Orch->>DB: check runs.transfer_bc_from_run_hash
    Note over Orch: cascade upstream if needed (see diagram D)
```

## B. New ND runs (rows 3, 4, 5)

Model unchanged — re-run from ND.

```mermaid
sequenceDiagram
    actor Op as Operator
    participant DB as DB
    participant Orch as Orchestrator
    participant S3 as S3
    participant ND as run_nd_scenarios
    participant PS as plan_scenarios
    participant KWSE as run_kwse_scenarios

    Op->>DB: update desired_state (q_set, solver, or library_density) + bump revision

    Note over Orch: sensor tick
    Orch->>DB: query gap (applied_revision < revision)
    DB-->>Orch: reach R needs work
    Orch->>DB: set current_state.processing = TRUE

    Orch->>ND: submit job (reach R, q range)
    ND->>S3: write depth.tif
    ND->>S3: write run.json (PUT LAST)
    ND-->>Orch: done
    Orch->>S3: verify run.json exists
    Orch->>DB: update current_state (q_set)
    Orch->>DB: record run in runs table

    Orch->>PS: plan KWSE sweep (in-process)
    PS->>S3: list ND results
    PS-->>Orch: ScenarioSet

    Orch->>KWSE: submit job (reach R, scenarios)
    KWSE->>S3: write depth.tif
    KWSE->>S3: write run.json (PUT LAST)
    KWSE-->>Orch: done
    Orch->>S3: verify run.json exists
    Orch->>DB: update current_state (ds_min_kwse, ds_max_kwse)
    Orch->>DB: record run in runs table
    Orch->>DB: set applied_revision = revision, processing = FALSE

    Orch->>DB: query reach_network (upstream of R)
    Orch->>DB: check runs.transfer_bc_from_run_hash
    Note over Orch: cascade upstream if needed (see diagram D)
```

## C. Domain / DEM change (rows 6, 8)

Always rebuild model (new domain = new path). Skip ND if they already exist at the new model path.

```mermaid
sequenceDiagram
    actor Op as Operator
    participant DB as DB
    participant Orch as Orchestrator
    participant BM as build_model
    participant S3 as S3
    participant ND as run_nd_scenarios
    participant PS as plan_scenarios
    participant KWSE as run_kwse_scenarios

    Op->>DB: update desired_state (domain or DEM) + bump revision

    Note over Orch: sensor tick
    Orch->>DB: query gap (applied_revision < revision)
    DB-->>Orch: reach R needs work
    Orch->>DB: set current_state.processing = TRUE

    Orch->>BM: submit job (reach R)
    BM->>S3: write model artifacts
    BM->>S3: write manifest.json
    BM-->>Orch: done
    Orch->>S3: verify manifest.json exists
    Orch->>DB: update current_state (model_hash, model_identity_hash, domain_hash)

    Orch->>S3: check for existing ND runs at new model path
    alt ND runs don't exist
        Orch->>ND: submit job (reach R, q range)
        ND->>S3: write depth.tif
        ND->>S3: write run.json (PUT LAST)
        ND-->>Orch: done
        Orch->>S3: verify run.json exists
        Orch->>DB: update current_state (q_set)
        Orch->>DB: record run in runs table
    end

    Orch->>PS: plan KWSE sweep (in-process)
    PS->>S3: list ND results
    PS-->>Orch: ScenarioSet

    Orch->>KWSE: submit job (reach R, scenarios)
    KWSE->>S3: write depth.tif
    KWSE->>S3: write run.json (PUT LAST)
    KWSE-->>Orch: done
    Orch->>S3: verify run.json exists
    Orch->>DB: update current_state (ds_min_kwse, ds_max_kwse)
    Orch->>DB: record run in runs table
    Orch->>DB: set applied_revision = revision, processing = FALSE

    Orch->>DB: query reach_network (upstream of R)
    Orch->>DB: check runs.transfer_bc_from_run_hash
    Note over Orch: cascade upstream if needed (see diagram D)
```

## D. Upstream cascade (row 9)

After downstream reach R completes, process each affected upstream reach. Upstream `desired_state.revision` is NOT bumped.

```mermaid
sequenceDiagram
    participant DB as DB
    participant Orch as Orchestrator
    participant BM as build_model
    participant S3 as S3
    participant ND as run_nd_scenarios
    participant PS as plan_scenarios
    participant KWSE as run_kwse_scenarios

    Note over Orch: reach R just completed

    Orch->>DB: query reach_network (upstream neighbors of R)
    Orch->>DB: check runs.transfer_bc_from_run_hash for each candidate
    DB-->>Orch: affected upstream reaches (U₁, U₂, ...)

    loop for each affected upstream reach U
        Orch->>DB: set current_state.processing = TRUE (reach U)

        Orch->>S3: check model exists at expected path for U
        alt model doesn't exist
            Orch->>BM: submit job (reach U)
            BM->>S3: write model artifacts
            BM->>S3: write manifest.json
            BM-->>Orch: done
            Orch->>S3: verify manifest.json exists
            Orch->>DB: update current_state (model_hash, model_identity_hash, domain_hash)
        end

        Orch->>S3: check for existing ND runs at model path for U
        alt ND runs don't exist
            Orch->>ND: submit job (reach U, q range)
            ND->>S3: write depth.tif
            ND->>S3: write run.json (PUT LAST)
            ND-->>Orch: done
            Orch->>S3: verify run.json exists
            Orch->>DB: update current_state (q_set)
            Orch->>DB: record run in runs table
        end

        Orch->>PS: plan KWSE sweep (in-process)
        PS->>S3: list ND results
        PS-->>Orch: ScenarioSet

        Orch->>KWSE: submit job (reach U, scenarios)
        KWSE->>S3: write depth.tif
        KWSE->>S3: write run.json (PUT LAST)
        KWSE-->>Orch: done
        Orch->>S3: verify run.json exists
        Orch->>DB: update current_state (ds_min_kwse, ds_max_kwse)
        Orch->>DB: record run in runs table
        Orch->>DB: set current_state.processing = FALSE (reach U)

        Note over Orch: same cascade logic applies to U's upstream neighbors
    end
```

