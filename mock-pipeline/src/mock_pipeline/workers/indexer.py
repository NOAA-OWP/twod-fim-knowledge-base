"""Pipeline-owned. Reads run.manifest.json and upserts catalog rows."""

from __future__ import annotations

import json
from pathlib import Path

from mock_pipeline.catalog.sqlite_catalog import SQLiteCatalog
from mock_pipeline.contracts import IndexerResult

_UPSERT_KEYS = ["reach_id", "model_manifest_hash", "run_hash", "q_label", "kwse_label"]


def indexer(
    run_manifest_uri: str,
    *,
    catalog: SQLiteCatalog,
    root: Path,
) -> IndexerResult:
    manifest = json.loads((root / run_manifest_uri).read_text())

    row = {
        "reach_id": manifest["reach_id"],
        "model_manifest_hash": manifest["model_manifest_hash"],
        "run_hash": manifest["run_hash"],
        "run_type": manifest["run_type"],
        "q_label": manifest["scenario"]["q_label"],
        "kwse_label": manifest["scenario"]["kwse_label"],
        "depth_uri": manifest["outputs"]["depth_tif"],
        "converged": int(manifest["execution"]["converged"]),
        "wall_seconds": manifest["execution"].get("wall_seconds"),
    }

    catalog.upsert("runs", row, keys=_UPSERT_KEYS)

    return IndexerResult(
        run_manifest_uri=run_manifest_uri,
        table="runs",
        rows_upserted=1,
        status="upserted",
    )
