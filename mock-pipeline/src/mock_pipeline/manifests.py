"""Tooling placeholder — hash rules move to tooling repo when it exists."""

from __future__ import annotations

import hashlib
import json
from typing import Any

_EXCLUDED_MODEL = frozenset({"outputs", "created_at", "built_by"})
_EXCLUDED_RUN = frozenset({"outputs", "execution", "created_at"})


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def content_hash(canonical: str) -> str:
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def model_manifest_hash(manifest: dict[str, Any]) -> str:
    hashable = {k: v for k, v in manifest.items() if k not in _EXCLUDED_MODEL}
    return content_hash(canonical_json(hashable))


def run_manifest_hash(manifest: dict[str, Any]) -> str:
    hashable = {k: v for k, v in manifest.items() if k not in _EXCLUDED_RUN}
    return content_hash(canonical_json(hashable))


def scenario_set_hash(orders: list[tuple[str, float, str, float]]) -> str:
    return content_hash(canonical_json(sorted(orders)))
