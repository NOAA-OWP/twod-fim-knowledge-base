"""Single-reach E2E demo — wires the full chain without Dagster."""

from __future__ import annotations

import shutil
from pathlib import Path

from mock_pipeline.catalog.sqlite_catalog import SQLiteCatalog
from mock_pipeline.contracts import (
    BoundaryCondition,
    DemSource,
    DomainSpec,
    HydrofabricRef,
    KwseStrategy,
    RoughnessSource,
    SolverSpec,
)
from mock_pipeline.workers.indexer import indexer
from mock_pipeline.workers.reach_build import reach_build
from mock_pipeline.workers.reach_scenario_run import reach_scenario_run
from mock_pipeline.workers.reach_scenario_set import reach_scenario_set

REACH_ID = 12345

HYDROFABRIC = HydrofabricRef(source="NextGen", snapshot="v2.2-conus", vpu=1)
DEM = DemSource(source="USGS_3DEP", snapshot_date="2026-04-01", resolution_m=10)
ROUGHNESS = RoughnessSource(source="MRLC_NLCD", snapshot_date="2026-04-01")
DOMAIN = DomainSpec(resolution_m=10, bbox_5070=(-95.10, 30.50, -94.90, 30.70))
SOLVER = SolverSpec(
    engine="LISFLOOD-FP", solver_kind="acceleration",
    use_cuda=True, image="lisflood-fp:latest-gpu@sha256:abc123", engine_version="8.0-ngwpc",
)
KWSE_STRATEGY = KwseStrategy(kind="uniform_sweep", step_ft=0.1, min_ft=2.5, max_ft=2.8)


def run_demo(root: Path, catalog_path: Path, *, sleep_seconds: float = 0.5) -> SQLiteCatalog:
    # 1. reach_build
    build_result = reach_build(
        REACH_ID,
        hydrofabric_ref=HYDROFABRIC,
        dem_source=DEM,
        roughness_source=ROUGHNESS,
        overrides=[],
        domain=DOMAIN,
        twodimfim_version="0.3.1",
        sdr_commit="abc1234567890def",
        root=root,
    )
    print(f"[reach_build] reach={REACH_ID} hash={build_result.manifest_hash} status={build_result.status}")

    # 2. ND run
    nd_result = reach_scenario_run(
        REACH_ID,
        build_result.manifest_hash,
        run_type="nd",
        q_label="Q100",
        q_value_cms=200.0,
        kwse_label="ND",
        kwse_value_ft=0.0,
        boundary_conditions=[
            BoundaryCondition(location="us_bc_line", kind="QFIX", value=200.0, units="cms"),
        ],
        solver=SOLVER,
        hotstart_uri=None,
        root=root,
        sleep_seconds=sleep_seconds,
    )
    print(f"[reach_scenario_run] ND reach={REACH_ID} q=Q100 status={nd_result.status}")

    # 3. Scenario planning
    scenario_set = reach_scenario_set(
        REACH_ID,
        build_result.manifest_hash,
        aep_targets=["Q100"],
        kwse_strategy=KWSE_STRATEGY,
        root=root,
    )
    print(f"[reach_scenario_set] reach={REACH_ID} n_scenarios={len(scenario_set.orders)}")

    # 4. KWSE runs
    kwse_uris: list[str] = []
    for order in scenario_set.orders:
        run_result = reach_scenario_run(
            REACH_ID,
            build_result.manifest_hash,
            run_type="kwse",
            q_label=order.q_label,
            q_value_cms=order.q_value_cms,
            kwse_label=order.kwse_label,
            kwse_value_ft=order.kwse_value_ft,
            boundary_conditions=[
                BoundaryCondition(location="us_bc_line", kind="QFIX", value=order.q_value_cms, units="cms"),
                BoundaryCondition(location="transfer_line", kind="HFIX", value=order.kwse_value_ft, units="ft"),
            ],
            solver=SOLVER,
            hotstart_uri=order.hotstart_uri,
            root=root,
            sleep_seconds=sleep_seconds,
        )
        kwse_uris.append(run_result.run_manifest_uri)
        print(f"[reach_scenario_run] KWSE reach={REACH_ID} q={order.q_label} kwse={order.kwse_label} status={run_result.status}")

    # 5. Index ND + all KWSE runs
    catalog = SQLiteCatalog(catalog_path)
    indexer(nd_result.run_manifest_uri, catalog=catalog, root=root)
    print(f"[indexer] ND indexed")
    for uri in kwse_uris:
        indexer(uri, catalog=catalog, root=root)
    print(f"[indexer] {len(kwse_uris)} KWSE runs indexed")

    # 6. Query catalog
    rows = catalog.query("SELECT reach_id, run_type, q_label, kwse_label, converged FROM runs ORDER BY run_type, kwse_label")
    print(f"\n--- Catalog ({len(rows)} rows) ---")
    for row in rows:
        print(f"  reach={row['reach_id']} type={row['run_type']} q={row['q_label']} kwse={row['kwse_label']} converged={row['converged']}")

    return catalog


def main() -> None:
    root = Path("./s3")
    catalog_path = Path("./catalog/catalog.sqlite")

    if root.exists():
        shutil.rmtree(root)
    if catalog_path.exists():
        catalog_path.unlink()

    print("=== Single-reach E2E demo ===\n")
    run_demo(root, catalog_path)
    print("\n=== Done ===")


if __name__ == "__main__":
    main()
