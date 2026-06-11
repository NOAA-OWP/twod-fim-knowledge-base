# process_build_model

## Overview

Orchestrator function that wraps the `build_model` worker. Reads desired state from DB, constructs worker inputs, submits the job, verifies artifacts, and updates current state. For worker I/O details (inputs, artifacts, checks, errors), see [`build_model-design.md`](build_model-design.md) and [`model.schema.json`](model.schema.json) ([PR #101](https://github.com/NGWPC/twod-fim-knowledge-base/pull/101)).

## Function Signature

```python
def process_build_model(reach_id: int, state_store: StateStore, config: PipelineConfig) -> BuildResult:
    """
    Orchestrator wrapper for build_model worker.

    Args:
        reach_id: Reach to build model for.
        state_store: Orchestrator DB access layer (reads desired_state, writes current_state).
                     Never passed to the worker.
        config: System-wide settings (db_uri, store_root, optional defaults).
                Never passed to the worker as-is — individual fields extracted.

    Returns:
        BuildResult with identity_hash and model_id from the worker response.
    """
```

## Input Mapping

How the orchestrator constructs worker inputs from DB state + config:

| Worker input | Source | How orchestrator provides it |
|---|---|---|
| `reach_id` | `desired_state.reach_id` | Direct from DB |
| `db_uri` | Orchestrator config | System-wide env var. Worker reads `reach_network` table (static, read-only). |
| `base_output_path` | Constructed | `{store_root}/version=v{MAJOR}/models/reach={reach_id}/` |
| `dem_source` | Orchestrator config | Optional — worker has default. Pass only if overriding. |
| `roughness_source` | Orchestrator config | Optional — worker has default. Pass only if overriding. |
| `other_geometries` | — | `None` for initial implementation. Domain expansion is `expand_model` scope. |
| All other optionals | Orchestrator config | System-wide defaults: `domain_buffer`, `grid_resolution`, `walk_us_dist_pct`, `epsg_code`, `bankfull_width_multiplier`, `lulc_lookup` |

## Processing Steps

1. Read `desired_state` for the reach.
2. Construct `base_output_path` from `store_root` + S3 path conventions.
3. Submit `build_model` job to worker container with constructed inputs.
4. Wait for job completion.
5. On success: verify `model.json` exists at `base_output_path/{model_id}/`.
6. Update `current_state`: `model_id`, `identity_hash`, `domain_code`.

## Output Mapping

How the orchestrator maps the worker response back to DB state:

| Worker response | `current_state` column | Notes |
|---|---|---|
| `identity_hash` | `identity_hash` | Direct |
| `model_id` | `model_id` | identity_hash + domain_code (e.g., `a3f9c1e8+N200S200E300W200`) |
| (derived from `model_id`) | `domain_code` | Portion after `+` separator |

No `runs` table entry — `build_model` produces a model, not a run.

## Error Handling

On worker error, the orchestrator logs the error. Gap still exists — reconciliation loop retries on next tick.

| Failure mode | Orchestrator action |
|---|---|
| Container crash / timeout | Log error. Gap persists — loop retries. |
| Worker raises error (e.g., `DatasetUnavailableError`) | Log error + error type. Gap persists — loop retries. |
| Verification failure (`model.json` missing after success exit) | Log as unexpected. Gap persists — loop retries. |
| DB update failure (job succeeded but state write fails) | Log error. `model.json` exists on S3 — next retry will see it via worker idempotency check and return immediately. |

## Execution

- **Runtime:** ~10 seconds per reach.
- **Execution mode:** Local container (not AWS Batch — overhead is expensive).
- **Execution backend:** Decision deferred to implementation. Options: `dagster-docker`, Dagster Pipes, direct subprocess.

## Out of Scope

- Model expansion (`expand_model` — separate entrypoint, separate function).
- Scenario generation, solver runs.
- Worker I/O details (see [`build_model-design.md`](build_model-design.md) + [`model.schema.json`](model.schema.json), [PR #101](https://github.com/NGWPC/twod-fim-knowledge-base/pull/101)).
