"""Pipeline-owned. KWSE sweep planner — discovers ND results, generates scenarios in-memory."""

from __future__ import annotations

import json
from pathlib import Path

from mock_pipeline.contracts import KwseStrategy, ScenarioOrder, ScenarioSet
from mock_pipeline.manifests import scenario_set_hash
from mock_pipeline.s3_paths import result_dir


def reach_scenario_set(
    reach_id: int,
    model_manifest_hash: str,
    *,
    aep_targets: list[str],
    kwse_strategy: KwseStrategy,
    root: Path,
) -> ScenarioSet:
    nd_results = _discover_nd_results(root, reach_id, model_manifest_hash, aep_targets)
    orders = _generate_sweep(reach_id, model_manifest_hash, nd_results, kwse_strategy)

    tuples = [(o.q_label, o.q_value_cms, o.kwse_label, o.kwse_value_ft) for o in orders]
    return ScenarioSet(
        reach_id=reach_id,
        model_manifest_hash=model_manifest_hash,
        scenario_set_hash=scenario_set_hash(tuples),
        orders=orders,
    )


def _discover_nd_results(
    root: Path, reach_id: int, model_manifest_hash: str, aep_targets: list[str],
) -> list[dict]:
    pattern = f"version=v*/results/reach={reach_id}/{model_manifest_hash}/*/q=*/kwse=ND/run.manifest.json"
    results = []
    for manifest_path in root.glob(pattern):
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("scenario", {}).get("q_label") in aep_targets:
            results.append(manifest["scenario"])
    results.sort(key=lambda s: s["q_label"])
    return results


def _generate_sweep(
    reach_id: int,
    model_manifest_hash: str,
    nd_results: list[dict],
    strategy: KwseStrategy,
) -> list[ScenarioOrder]:
    kwse_values = _kwse_range(strategy)
    orders: list[ScenarioOrder] = []

    for nd in nd_results:
        q_label = nd["q_label"]
        q_value_cms = nd["q_value_cms"]
        prev_uri: str | None = None

        for kwse_ft in kwse_values:
            kwse_label = f"{kwse_ft:.1f}"
            order = ScenarioOrder(
                q_label=q_label,
                q_value_cms=q_value_cms,
                kwse_label=kwse_label,
                kwse_value_ft=kwse_ft,
                hotstart_uri=prev_uri,
            )
            orders.append(order)
            # run_hash unknown until reach_scenario_run computes it; orchestrator resolves
            prev_uri = str(
                result_dir(reach_id, model_manifest_hash, "PENDING", q_label, kwse_label)
                / "depth.tif"
            )

    return orders


def _kwse_range(strategy: KwseStrategy) -> list[float]:
    values = []
    v = strategy.min_ft
    while v <= strategy.max_ft + 1e-6:
        values.append(round(v, 6))
        v += strategy.step_ft
    return values
