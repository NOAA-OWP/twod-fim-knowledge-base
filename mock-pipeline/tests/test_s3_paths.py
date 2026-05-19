from mock_pipeline.s3_paths import (
    model_dir,
    model_manifest_path,
    override_dir,
    result_dir,
    run_manifest_path,
)


def test_override_dir():
    assert str(override_dir(12345, "2026-05-01_levee-fix")) == (
        "version=v1/overrides/reach=12345/2026-05-01_levee-fix"
    )


def test_model_dir():
    assert str(model_dir(12345, "f4a9bc12d6e80f3a")) == (
        "version=v1/models/reach=12345/f4a9bc12d6e80f3a"
    )


def test_model_manifest_path():
    assert str(model_manifest_path(12345, "f4a9bc12d6e80f3a")) == (
        "version=v1/models/reach=12345/f4a9bc12d6e80f3a/manifest.json"
    )


def test_result_dir():
    assert str(result_dir(12345, "f4a9bc12d6e80f3a", "1c8e44b9a2305f7d", "Q100", "2.5")) == (
        "version=v1/results/reach=12345/f4a9bc12d6e80f3a/1c8e44b9a2305f7d/q=Q100/kwse=2.5"
    )


def test_run_manifest_path():
    assert str(run_manifest_path(12345, "f4a9bc12d6e80f3a", "1c8e44b9a2305f7d", "Q100", "2.5")) == (
        "version=v1/results/reach=12345/f4a9bc12d6e80f3a/1c8e44b9a2305f7d/q=Q100/kwse=2.5/run.manifest.json"
    )
