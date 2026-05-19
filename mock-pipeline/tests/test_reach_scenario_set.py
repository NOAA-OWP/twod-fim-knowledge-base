import json

from mock_pipeline.contracts import KwseStrategy
from mock_pipeline.s3_paths import run_manifest_path
from mock_pipeline.workers.reach_scenario_set import reach_scenario_set

REACH_ID = 12345
MODEL_HASH = "f4a9bc12d6e80f3a"
ND_RUN_HASH = "aabbccdd11223344"
STRATEGY = KwseStrategy(kind="uniform_sweep", step_ft=0.5, min_ft=2.0, max_ft=3.0)


def _create_nd_result(root, q_label, q_value_cms):
    """Write a minimal ND run.manifest.json so reach_scenario_set can discover it."""
    manifest = {
        "schema_version": 1,
        "reach_id": REACH_ID,
        "model_manifest_hash": MODEL_HASH,
        "run_hash": ND_RUN_HASH,
        "run_type": "nd",
        "scenario": {
            "q_label": q_label,
            "q_value_cms": q_value_cms,
            "kwse_label": "ND",
            "kwse_value_ft": 0.0,
        },
    }
    path = root / run_manifest_path(REACH_ID, MODEL_HASH, ND_RUN_HASH, q_label, "ND")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest))


def test_discovers_nd_and_generates_sweep(tmp_path):
    _create_nd_result(tmp_path, "Q100", 200.0)

    result = reach_scenario_set(
        REACH_ID, MODEL_HASH, aep_targets=["Q100"], kwse_strategy=STRATEGY, root=tmp_path,
    )

    assert len(result.orders) == 3
    kwse_values = [o.kwse_value_ft for o in result.orders]
    assert kwse_values == [2.0, 2.5, 3.0]
    assert all(o.q_label == "Q100" for o in result.orders)
    assert all(o.q_value_cms == 200.0 for o in result.orders)


def test_hotstart_chain(tmp_path):
    _create_nd_result(tmp_path, "Q100", 200.0)

    result = reach_scenario_set(
        REACH_ID, MODEL_HASH, aep_targets=["Q100"], kwse_strategy=STRATEGY, root=tmp_path,
    )

    assert result.orders[0].hotstart_uri is None
    for i in range(1, len(result.orders)):
        assert result.orders[i].hotstart_uri is not None
        assert "depth.tif" in result.orders[i].hotstart_uri


def test_deterministic_hash(tmp_path):
    _create_nd_result(tmp_path, "Q100", 200.0)

    first = reach_scenario_set(
        REACH_ID, MODEL_HASH, aep_targets=["Q100"], kwse_strategy=STRATEGY, root=tmp_path,
    )
    second = reach_scenario_set(
        REACH_ID, MODEL_HASH, aep_targets=["Q100"], kwse_strategy=STRATEGY, root=tmp_path,
    )

    assert first.scenario_set_hash == second.scenario_set_hash
