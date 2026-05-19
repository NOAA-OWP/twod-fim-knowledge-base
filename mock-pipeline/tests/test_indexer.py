from mock_pipeline.catalog.sqlite_catalog import SQLiteCatalog
from mock_pipeline.contracts import BoundaryCondition, SolverSpec
from mock_pipeline.workers.indexer import indexer
from mock_pipeline.workers.reach_scenario_run import reach_scenario_run

_SOLVER = SolverSpec(
    engine="LISFLOOD-FP", solver_kind="acceleration",
    use_cuda=True, image="lisflood-fp:latest-gpu@sha256:abc123", engine_version="8.0-ngwpc",
)


def _run_and_get_uri(tmp_path):
    result = reach_scenario_run(
        reach_id=12345,
        model_manifest_hash="f4a9bc12d6e80f3a",
        run_type="kwse",
        q_label="Q100",
        q_value_cms=200.0,
        kwse_label="2.5",
        kwse_value_ft=2.5,
        boundary_conditions=[
            BoundaryCondition(location="us_bc_line", kind="QFIX", value=200.0, units="cms"),
        ],
        solver=_SOLVER,
        hotstart_uri=None,
        root=tmp_path,
        sleep_seconds=0,
    )
    return result.run_manifest_uri


def test_indexes_run_manifest(tmp_path):
    uri = _run_and_get_uri(tmp_path)
    catalog = SQLiteCatalog(tmp_path / "catalog.sqlite")

    result = indexer(uri, catalog=catalog, root=tmp_path)
    assert result.rows_upserted == 1
    assert result.status == "upserted"

    rows = catalog.query("SELECT * FROM runs WHERE reach_id = ?", (12345,))
    assert len(rows) == 1
    assert rows[0]["q_label"] == "Q100"
    assert rows[0]["kwse_label"] == "2.5"
    assert rows[0]["converged"] == 1


def test_indexed_at_populated(tmp_path):
    uri = _run_and_get_uri(tmp_path)
    catalog = SQLiteCatalog(tmp_path / "catalog.sqlite")

    indexer(uri, catalog=catalog, root=tmp_path)

    rows = catalog.query("SELECT indexed_at FROM runs", ())
    assert rows[0]["indexed_at"] is not None
