"""Tooling placeholder — path builders move to tooling repo when it exists."""

from __future__ import annotations

from pathlib import PurePosixPath


def _version_prefix(major: int) -> PurePosixPath:
    return PurePosixPath(f"version=v{major}")


def override_dir(reach_id: int, override_name: str, *, major: int = 1) -> PurePosixPath:
    return _version_prefix(major) / "overrides" / f"reach={reach_id}" / override_name


def model_dir(reach_id: int, manifest_hash: str, *, major: int = 1) -> PurePosixPath:
    return _version_prefix(major) / "models" / f"reach={reach_id}" / manifest_hash


def model_manifest_path(reach_id: int, manifest_hash: str, *, major: int = 1) -> PurePosixPath:
    return model_dir(reach_id, manifest_hash, major=major) / "manifest.json"


def result_dir(
    reach_id: int,
    model_manifest_hash: str,
    run_hash: str,
    q_label: str,
    kwse_label: str,
    *,
    major: int = 1,
) -> PurePosixPath:
    return (
        _version_prefix(major)
        / "results"
        / f"reach={reach_id}"
        / model_manifest_hash
        / run_hash
        / f"q={q_label}"
        / f"kwse={kwse_label}"
    )


def run_manifest_path(
    reach_id: int,
    model_manifest_hash: str,
    run_hash: str,
    q_label: str,
    kwse_label: str,
    *,
    major: int = 1,
) -> PurePosixPath:
    return result_dir(reach_id, model_manifest_hash, run_hash, q_label, kwse_label, major=major) / "run.manifest.json"
