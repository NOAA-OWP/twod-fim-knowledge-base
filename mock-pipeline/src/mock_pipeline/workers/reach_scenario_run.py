"""Tooling placeholder — mock stub for reach_scenario_run. Replaced by tooling repo when it exists."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from mock_pipeline.contracts import BoundaryCondition, RunResult, SolverSpec
from mock_pipeline.manifests import run_manifest_hash
from mock_pipeline.s3_paths import result_dir, run_manifest_path
from mock_pipeline.stubs.fake_rasters import write_placeholder


def reach_scenario_run(
    reach_id: int,
    model_manifest_hash: str,
    run_type: Literal["nd", "kwse"],
    q_label: str,
    q_value_cms: float,
    kwse_label: str,
    kwse_value_ft: float,
    boundary_conditions: list[BoundaryCondition],
    solver: SolverSpec,
    hotstart_uri: str | None,
    *,
    root: Path,
    sleep_seconds: float = 0.5,
) -> RunResult:
    manifest = _build_manifest_dict(
        reach_id, model_manifest_hash, run_type,
        q_label, q_value_cms, kwse_label, kwse_value_ft,
        boundary_conditions, solver,
    )
    rhash = run_manifest_hash(manifest)

    manifest_file = root / run_manifest_path(
        reach_id, model_manifest_hash, rhash, q_label, kwse_label,
    )
    if manifest_file.exists():
        return RunResult(
            reach_id=reach_id,
            model_manifest_hash=model_manifest_hash,
            run_hash=rhash,
            run_manifest_uri=str(run_manifest_path(reach_id, model_manifest_hash, rhash, q_label, kwse_label)),
            status="reused",
            converged=True,
        )

    target = root / result_dir(reach_id, model_manifest_hash, rhash, q_label, kwse_label)

    # Mimics the hydraulic modeling step (2D Model in production)
    if sleep_seconds > 0:
        time.sleep(sleep_seconds)

    # All artifacts written before manifest — PUT-last ordering.
    # Indexer uses run.manifest.json presence as the completion signal.
    write_placeholder(target / "depth.tif")

    manifest["run_hash"] = rhash
    manifest["execution"] = _stub_execution(hotstart_uri)
    manifest["outputs"] = {"depth_tif": str(target / "depth.tif")}
    manifest["created_at"] = datetime.now(timezone.utc).isoformat()

    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2))

    return RunResult(
        reach_id=reach_id,
        model_manifest_hash=model_manifest_hash,
        run_hash=rhash,
        run_manifest_uri=str(run_manifest_path(reach_id, model_manifest_hash, rhash, q_label, kwse_label)),
        status="completed",
        converged=True,
    )


def _build_manifest_dict(
    reach_id: int,
    model_manifest_hash: str,
    run_type: str,
    q_label: str,
    q_value_cms: float,
    kwse_label: str,
    kwse_value_ft: float,
    boundary_conditions: list[BoundaryCondition],
    solver: SolverSpec,
) -> dict:
    return {
        "schema_version": 1,
        "reach_id": reach_id,
        "model_manifest_hash": model_manifest_hash,
        "run_type": run_type,
        "scenario": {
            "q_label": q_label,
            "q_value_cms": q_value_cms,
            "kwse_label": kwse_label,
            "kwse_value_ft": kwse_value_ft,
        },
        "boundary_conditions": [asdict(bc) for bc in boundary_conditions],
        "solver": asdict(solver),
    }


def _stub_execution(hotstart_uri: str | None) -> dict:
    return {
        "started_at": "2026-05-12T18:05:11Z",
        "ended_at": "2026-05-12T18:08:43Z",
        "wall_seconds": 212.3,
        "converged": True,
        "iterations": 6,
        "mass_balance_error": 0.0021,
        "hotstart_from": hotstart_uri,
    }
