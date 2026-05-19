import json

from mock_pipeline.contracts import BoundaryCondition, SolverSpec
from mock_pipeline.workers.reach_scenario_run import reach_scenario_run

COMMON_KWARGS = dict(
    reach_id=12345,
    model_manifest_hash="f4a9bc12d6e80f3a",
    run_type="kwse",
    q_label="Q100",
    q_value_cms=200.0,
    kwse_label="2.5",
    kwse_value_ft=2.5,
    boundary_conditions=[
        BoundaryCondition(location="us_bc_line", kind="QFIX", value=200.0, units="cms"),
        BoundaryCondition(location="transfer_line", kind="HFIX", value=2.5, units="ft"),
    ],
    solver=SolverSpec(
        engine="LISFLOOD-FP",
        solver_kind="acceleration",
        use_cuda=True,
        image="lisflood-fp:latest-gpu@sha256:abc123",
        engine_version="8.0-ngwpc",
    ),
    hotstart_uri=None,
    sleep_seconds=0,
)


def _result_dir(tmp_path, run_hash):
    return (
        tmp_path / "version=v1" / "results" / "reach=12345"
        / "f4a9bc12d6e80f3a" / run_hash / "q=Q100" / "kwse=2.5"
    )


def test_creates_expected_files(tmp_path):
    result = reach_scenario_run(**COMMON_KWARGS, root=tmp_path)
    assert result.status == "completed"
    assert result.converged is True

    rdir = _result_dir(tmp_path, result.run_hash)
    assert (rdir / "depth.tif").exists()
    assert (rdir / "run.manifest.json").exists()

    manifest = json.loads((rdir / "run.manifest.json").read_text())
    assert manifest["reach_id"] == 12345
    assert manifest["scenario"]["q_label"] == "Q100"
    assert "execution" in manifest
    assert "outputs" in manifest


def test_idempotent_reuse(tmp_path):
    first = reach_scenario_run(**COMMON_KWARGS, root=tmp_path)
    second = reach_scenario_run(**COMMON_KWARGS, root=tmp_path)
    assert first.run_hash == second.run_hash
    assert second.status == "reused"


def test_put_last_ordering(tmp_path):
    result = reach_scenario_run(**COMMON_KWARGS, root=tmp_path)
    rdir = _result_dir(tmp_path, result.run_hash)
    depth_mtime = (rdir / "depth.tif").stat().st_mtime
    manifest_mtime = (rdir / "run.manifest.json").stat().st_mtime
    assert manifest_mtime >= depth_mtime
