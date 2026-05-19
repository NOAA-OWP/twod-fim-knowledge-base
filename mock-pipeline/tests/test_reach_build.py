import json

from mock_pipeline.contracts import (
    DemSource,
    DomainSpec,
    HydrofabricRef,
    OverrideRef,
    RoughnessSource,
)
from mock_pipeline.workers.reach_build import reach_build

COMMON_KWARGS = dict(
    reach_id=12345,
    hydrofabric_ref=HydrofabricRef(source="NextGen", snapshot="v2.2-conus", vpu=1),
    dem_source=DemSource(source="USGS_3DEP", snapshot_date="2026-04-01", resolution_m=10),
    roughness_source=RoughnessSource(source="MRLC_NLCD", snapshot_date="2026-04-01"),
    overrides=[OverrideRef(name="2026-05-01_levee-fix")],
    domain=DomainSpec(resolution_m=10, bbox_5070=(-95.10, 30.50, -94.90, 30.70)),
    twodimfim_version="0.3.1",
    sdr_commit="abc1234567890def",
)

EXPECTED_FILES = [
    "manifest.json",
    "rasters/dem.tif",
    "rasters/roughness.tif",
    "vectors/divide.geojson",
    "vectors/centerline.geojson",
    "vectors/us_bc_line.geojson",
    "vectors/transfer_line.geojson",
]


def test_creates_expected_files(tmp_path):
    result = reach_build(**COMMON_KWARGS, root=tmp_path)
    assert result.status == "built"

    model_dir = tmp_path / "version=v1" / "models" / "reach=12345" / result.manifest_hash
    for name in EXPECTED_FILES:
        assert (model_dir / name).exists(), f"missing {name}"

    manifest = json.loads((model_dir / "manifest.json").read_text())
    assert manifest["reach_id"] == 12345
    assert "outputs" in manifest
    assert "inputs" in manifest


def test_idempotent_reuse(tmp_path):
    first = reach_build(**COMMON_KWARGS, root=tmp_path)
    second = reach_build(**COMMON_KWARGS, root=tmp_path)
    assert first.manifest_hash == second.manifest_hash
    assert second.status == "reused"


def test_override_changes_hash(tmp_path):
    first = reach_build(**COMMON_KWARGS, root=tmp_path)
    modified_kwargs = {**COMMON_KWARGS, "overrides": []}
    second = reach_build(**modified_kwargs, root=tmp_path)
    assert first.manifest_hash != second.manifest_hash
