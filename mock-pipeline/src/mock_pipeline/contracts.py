from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# --- Pipeline-owned types ---


@dataclass(frozen=True)
class ReachBuildResult:
    reach_id: int
    manifest_hash: str
    model_manifest_uri: str
    status: Literal["built", "reused"]


@dataclass(frozen=True)
class KwseStrategy:
    kind: Literal["uniform_sweep", "adaptive"]
    step_ft: float = 0.1
    min_ft: float = 0.0
    max_ft: float = 10.0


@dataclass(frozen=True)
class ScenarioOrder:
    q_label: str
    q_value_cms: float
    kwse_label: str
    kwse_value_ft: float
    hotstart_uri: str | None


@dataclass(frozen=True)
class ScenarioSet:
    reach_id: int
    model_manifest_hash: str
    scenario_set_hash: str
    orders: list[ScenarioOrder]


@dataclass(frozen=True)
class RunResult:
    reach_id: int
    model_manifest_hash: str
    run_hash: str
    run_manifest_uri: str
    status: Literal["completed", "reused"]
    converged: bool


@dataclass(frozen=True)
class CatalogSourceRule:
    prefix_pattern: str
    on_event: Literal["ObjectCreated", "ObjectRemoved"]
    target_table: str
    field_mapping: dict[str, str]
    upsert_keys: list[str]


@dataclass(frozen=True)
class RetentionRules:
    derived_data_days: int = 30


@dataclass(frozen=True)
class CatalogPolicy:
    sources: list[CatalogSourceRule]
    retention: RetentionRules


@dataclass(frozen=True)
class IndexerResult:
    run_manifest_uri: str
    table: str
    rows_upserted: int
    status: Literal["upserted", "skipped"]


# --- Tooling placeholders (move when tooling repo exists) ---


@dataclass(frozen=True)
class HydrofabricRef:
    source: str
    snapshot: str
    vpu: int


@dataclass(frozen=True)
class DemSource:
    source: str
    snapshot_date: str
    resolution_m: int


@dataclass(frozen=True)
class RoughnessSource:
    source: str
    snapshot_date: str


@dataclass(frozen=True)
class OverrideRef:
    name: str


@dataclass(frozen=True)
class DomainSpec:
    resolution_m: int
    bbox_5070: tuple[float, float, float, float]
    crs: str = "EPSG:5070"


@dataclass(frozen=True)
class BoundaryCondition:
    location: str
    kind: Literal["QFIX", "HFIX", "FREE", "TRANSFER"]
    value: float
    units: str
    source: dict | None = None


@dataclass(frozen=True)
class SolverSpec:
    engine: str
    solver_kind: str
    use_cuda: bool
    image: str
    engine_version: str
