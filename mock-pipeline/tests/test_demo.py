from mock_pipeline.demo import run_demo


def test_e2e_single_reach(tmp_path):
    catalog = run_demo(tmp_path / "s3", tmp_path / "catalog.sqlite", sleep_seconds=0)

    rows = catalog.query("SELECT * FROM runs ORDER BY run_type, kwse_label")

    assert len(rows) == 5
    nd_rows = [r for r in rows if r["run_type"] == "nd"]
    kwse_rows = [r for r in rows if r["run_type"] == "kwse"]
    assert len(nd_rows) == 1
    assert len(kwse_rows) == 4
    assert nd_rows[0]["q_label"] == "Q100"
    assert nd_rows[0]["kwse_label"] == "ND"
    assert all(r["converged"] == 1 for r in rows)
    kwse_labels = sorted(r["kwse_label"] for r in kwse_rows)
    assert kwse_labels == ["2.5", "2.6", "2.7", "2.8"]
