# 2D FIM Mock Pipeline

Mock implementation of the 2D FIM CONUS pipeline. Stub-with-fake-artifacts fidelity: workers write 1-byte placeholder rasters + valid JSON manifests; the indexer upserts a real SQLite catalog. Content-addressed paths and idempotent workers.

## Quick start

```bash
uv sync                               # install (editable + dev deps)
uv run pytest tests/ -v               # runs tests
uv run python -m mock_pipeline.demo   # runs the single-reach E2E chain
```

The demo runs: `reach_build → ND run → scenario planner → 4 KWSE runs → indexer → catalog query`, then prints all catalog rows.

## Modules

| Module | Owner | What it does |
|---|---|---|
| `manifests.py` | Tooling placeholder | Canonical JSON + sha256 content hashing |
| `s3_paths.py` | Tooling placeholder | Path builders (PurePosixPath) for S3 layout |
| `contracts.py` | Mixed | 16 frozen dataclasses (9 pipeline, 7 tooling placeholder) |
| `stubs/fake_rasters.py` | Tooling placeholder | Writes 1-byte placeholder files |
| `workers/reach_build.py` | Tooling placeholder | Creates model manifest + placeholder rasters/vectors. Idempotent. |
| `workers/reach_scenario_run.py` | Tooling placeholder | Runs one scenario. PUT-last ordering (manifest after artifacts). Idempotent. |
| `workers/reach_scenario_set.py` | Pipeline | Discovers ND results, generates KWSE sweep, builds hotstart chain. No S3 writes. |
| `workers/indexer.py` | Pipeline (minimal) | Reads run.manifest.json, upserts SQLite. Hardcoded field extraction. |
| `catalog/sqlite_catalog.py` | Pipeline | SQLite catalog with upsert + query. `runs` table only. |
| `demo.py` | — | Wires the full chain without Dagster |

"Tooling placeholder" modules move to the tooling repo when it exists. "Pipeline" modules stay.
