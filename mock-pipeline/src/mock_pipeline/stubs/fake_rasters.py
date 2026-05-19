"""Tooling placeholder — real raster/vector generation moves to tooling repo when it exists."""

from __future__ import annotations

from pathlib import Path


def write_placeholder(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00")
