from mock_pipeline.catalog.sqlite_catalog import SQLiteCatalog


def test_upsert_and_query(tmp_path):
    catalog = SQLiteCatalog(tmp_path / "catalog.sqlite")
    row = {
        "reach_id": 12345,
        "model_manifest_hash": "f4a9bc12d6e80f3a",
        "run_hash": "1c8e44b9a2305f7d",
        "run_type": "kwse",
        "q_label": "Q100",
        "kwse_label": "2.5",
        "depth_uri": "results/reach=12345/.../depth.tif",
        "converged": 1,
        "wall_seconds": 212.3,
    }
    catalog.upsert("runs", row, keys=["reach_id", "model_manifest_hash", "run_hash", "q_label", "kwse_label"])

    rows = catalog.query("SELECT * FROM runs WHERE reach_id = ?", (12345,))
    assert len(rows) == 1
    assert rows[0]["q_label"] == "Q100"
    assert rows[0]["converged"] == 1


def test_upsert_idempotent(tmp_path):
    catalog = SQLiteCatalog(tmp_path / "catalog.sqlite")
    row = {
        "reach_id": 12345,
        "model_manifest_hash": "f4a9bc12d6e80f3a",
        "run_hash": "1c8e44b9a2305f7d",
        "run_type": "kwse",
        "q_label": "Q100",
        "kwse_label": "2.5",
        "depth_uri": "results/reach=12345/.../depth.tif",
        "converged": 1,
        "wall_seconds": 212.3,
    }
    keys = ["reach_id", "model_manifest_hash", "run_hash", "q_label", "kwse_label"]
    catalog.upsert("runs", row, keys=keys)
    catalog.upsert("runs", row, keys=keys)

    rows = catalog.query("SELECT * FROM runs", ())
    assert len(rows) == 1
