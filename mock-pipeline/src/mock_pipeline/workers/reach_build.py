"""Tooling placeholder — mock stub for reach_build. Replaced by tooling repo when it exists."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from mock_pipeline.contracts import (
    DemSource,
    DomainSpec,
    HydrofabricRef,
    OverrideRef,
    ReachBuildResult,
    RoughnessSource,
)
from mock_pipeline.manifests import model_manifest_hash
from mock_pipeline.s3_paths import model_dir, model_manifest_path, override_dir
from mock_pipeline.stubs.fake_rasters import write_placeholder

RASTERS = ["dem.tif", "roughness.tif"]
VECTORS = ["divide.geojson", "centerline.geojson", "us_bc_line.geojson", "transfer_line.geojson"]


def reach_build(
    reach_id: int,
    *,
    major_version: int = 1,
    hydrofabric_ref: HydrofabricRef,
    dem_source: DemSource,
    roughness_source: RoughnessSource,
    overrides: list[OverrideRef],
    domain: DomainSpec,
    twodimfim_version: str,
    sdr_commit: str,
    root: Path,
) -> ReachBuildResult:
    manifest = _build_manifest_dict(
        reach_id, major_version, hydrofabric_ref, dem_source,
        roughness_source, overrides, domain, twodimfim_version, sdr_commit,
    )
    mhash = model_manifest_hash(manifest)

    manifest_file = root / model_manifest_path(reach_id, mhash, major=major_version)
    if manifest_file.exists():
        return ReachBuildResult(
            reach_id=reach_id,
            manifest_hash=mhash,
            model_manifest_uri=str(model_manifest_path(reach_id, mhash, major=major_version)),
            status="reused",
        )

    target = root / model_dir(reach_id, mhash, major=major_version)

    for name in RASTERS:
        write_placeholder(target / "rasters" / name)
    for name in VECTORS:
        write_placeholder(target / "vectors" / name)

    manifest["outputs"] = _build_outputs(reach_id, mhash, major_version)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, indent=2))

    return ReachBuildResult(
        reach_id=reach_id,
        manifest_hash=mhash,
        model_manifest_uri=str(model_manifest_path(reach_id, mhash, major=major_version)),
        status="built",
    )


def _build_manifest_dict(
    reach_id: int,
    major_version: int,
    hydrofabric_ref: HydrofabricRef,
    dem_source: DemSource,
    roughness_source: RoughnessSource,
    overrides: list[OverrideRef],
    domain: DomainSpec,
    twodimfim_version: str,
    sdr_commit: str,
) -> dict:
    return {
        "schema_version": 1,
        "reach_id": reach_id,
        "version": {"major": major_version, "minor": 0, "sdr_commit": sdr_commit},
        "inputs": {
            "hydrofabric": asdict(hydrofabric_ref),
            "dem": asdict(dem_source),
            "roughness": asdict(roughness_source),
            "overrides": [
                {"name": o.name, "uri": str(override_dir(reach_id, o.name, major=major_version))}
                for o in overrides
            ],
        },
        "domain": asdict(domain),
        "twodimfim_version": twodimfim_version,
    }


def _build_outputs(reach_id: int, mhash: str, major: int) -> dict:
    base = str(model_dir(reach_id, mhash, major=major))
    return {
        "model_manifest_uri": f"{base}/manifest.json",
        "rasters": {name.removesuffix(".tif"): f"{base}/rasters/{name}" for name in RASTERS},
        "vectors": {name.removesuffix(".geojson"): f"{base}/vectors/{name}" for name in VECTORS},
    }
