import copy

import pytest

from mock_pipeline.manifests import (
    model_manifest_hash,
    run_manifest_hash,
    scenario_set_hash,
)


@pytest.fixture()
def model_manifest():
    return {
        "schema_version": 1,
        "reach_id": 12345,
        "version": {"major": 1, "minor": 2, "sdr_commit": "abc1234567890def"},
        "inputs": {
            "hydrofabric": {"source": "NextGen", "snapshot": "v2.2-conus", "vpu": 1},
            "dem": {"source": "USGS_3DEP", "snapshot_date": "2026-04-01", "resolution_m": 10},
            "roughness": {"source": "MRLC_NLCD", "snapshot_date": "2026-04-01"},
            "overrides": [
                {"name": "2026-05-01_levee-fix", "uri": "overrides/reach=12345/2026-05-01_levee-fix/"}
            ],
        },
        "domain": {"resolution_m": 10, "bbox_5070": [-95.10, 30.50, -94.90, 30.70], "crs": "EPSG:5070"},
        "twodimfim_version": "0.3.1",
        "outputs": {"model_manifest_uri": "models/reach=12345/HASH/manifest.json"},
        "created_at": "2026-05-12T18:00:00Z",
        "built_by": "reach_build@v0.1",
    }


@pytest.fixture()
def run_manifest():
    return {
        "schema_version": 1,
        "reach_id": 12345,
        "model_manifest_hash": "f4a9bc12d6e80f3a",
        "run_hash": "1c8e44b9a2305f7d",
        "run_type": "kwse",
        "scenario": {"q_label": "Q100", "q_value_cms": 200.0, "kwse_label": "2.5", "kwse_value_ft": 2.5},
        "boundary_conditions": [
            {"location": "us_bc_line", "kind": "QFIX", "value": 200.0, "units": "cms"},
            {
                "location": "transfer_line",
                "kind": "HFIX",
                "value": 2.5,
                "units": "ft",
                "source": {
                    "kind": "stage_transfer",
                    "from_reach_id": 12346,
                    "from_model_manifest_hash": "ab0e91d7c4c52ee0",
                    "from_run_hash": "7f3d29ae0b15ddc1",
                    "sampled_from": "results/reach=12346/.../q=Q100/kwse=2.5/depth.tif",
                },
            },
        ],
        "solver": {
            "engine": "LISFLOOD-FP",
            "solver_kind": "acceleration",
            "use_cuda": True,
            "image": "lisflood-fp:latest-gpu@sha256:abc123",
            "engine_version": "8.0-ngwpc",
        },
        "execution": {
            "started_at": "2026-05-12T18:05:11Z",
            "ended_at": "2026-05-12T18:08:43Z",
            "wall_seconds": 212.3,
            "converged": True,
            "iterations": 6,
            "mass_balance_error": 0.0021,
        },
        "outputs": {"depth_tif": "results/reach=12345/HASH/RUNHASH/q=Q100/kwse=2.5/depth.tif"},
        "created_at": "2026-05-12T18:08:44Z",
    }


class TestModelManifestHash:
    def test_excluded_fields_ignored(self, model_manifest):
        base = model_manifest_hash(model_manifest)
        modified = copy.deepcopy(model_manifest)
        modified["outputs"]["model_manifest_uri"] = "completely/different/path"
        modified["created_at"] = "2099-01-01T00:00:00Z"
        modified["built_by"] = "something_else@v9.9"
        assert model_manifest_hash(modified) == base

    def test_reach_id_changes_hash(self, model_manifest):
        base = model_manifest_hash(model_manifest)
        modified = copy.deepcopy(model_manifest)
        modified["reach_id"] = 99999
        assert model_manifest_hash(modified) != base

    def test_adding_override_changes_hash(self, model_manifest):
        base = model_manifest_hash(model_manifest)
        modified = copy.deepcopy(model_manifest)
        modified["inputs"]["overrides"].append(
            {"name": "2026-06-01_new-fix", "uri": "overrides/reach=12345/2026-06-01_new-fix/"}
        )
        assert model_manifest_hash(modified) != base


class TestRunManifestHash:
    def test_excluded_fields_ignored(self, run_manifest):
        base = run_manifest_hash(run_manifest)
        modified = copy.deepcopy(run_manifest)
        modified["outputs"]["depth_tif"] = "completely/different/path"
        modified["execution"]["wall_seconds"] = 9999.9
        modified["execution"]["converged"] = False
        modified["created_at"] = "2099-01-01T00:00:00Z"
        assert run_manifest_hash(modified) == base

    def test_scenario_changes_hash(self, run_manifest):
        base = run_manifest_hash(run_manifest)
        modified = copy.deepcopy(run_manifest)
        modified["scenario"]["q_value_cms"] = 500.0
        assert run_manifest_hash(modified) != base

    def test_boundary_conditions_change_hash(self, run_manifest):
        base = run_manifest_hash(run_manifest)
        modified = copy.deepcopy(run_manifest)
        modified["boundary_conditions"][0]["value"] = 999.0
        assert run_manifest_hash(modified) != base


class TestScenarioSetHash:
    def test_order_independent(self):
        a = [("Q100", 200.0, "2.5", 2.5), ("Q050", 100.0, "1.0", 1.0)]
        b = [("Q050", 100.0, "1.0", 1.0), ("Q100", 200.0, "2.5", 2.5)]
        assert scenario_set_hash(a) == scenario_set_hash(b)

    def test_content_sensitive(self):
        base = [("Q100", 200.0, "2.5", 2.5)]
        extended = base + [("Q050", 100.0, "1.0", 1.0)]
        assert scenario_set_hash(base) != scenario_set_hash(extended)
