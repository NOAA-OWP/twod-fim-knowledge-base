"""Pipeline-owned. SQLite implementation of the Catalog protocol for the mock."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_DDL = """
CREATE TABLE IF NOT EXISTS runs (
    reach_id              INTEGER NOT NULL,
    model_manifest_hash   TEXT    NOT NULL,
    run_hash              TEXT    NOT NULL,
    run_type              TEXT    NOT NULL CHECK (run_type IN ('nd', 'kwse')),
    q_label               TEXT    NOT NULL,
    kwse_label            TEXT    NOT NULL,
    depth_uri             TEXT    NOT NULL,
    converged             INTEGER NOT NULL,
    wall_seconds          REAL,
    indexed_at            TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (reach_id, model_manifest_hash, run_hash, q_label, kwse_label)
);

CREATE INDEX IF NOT EXISTS idx_runs_reach    ON runs (reach_id);
CREATE INDEX IF NOT EXISTS idx_runs_model    ON runs (reach_id, model_manifest_hash);
CREATE INDEX IF NOT EXISTS idx_runs_scenario ON runs (q_label, kwse_label);
"""


class SQLiteCatalog:
    def __init__(self, path: Path) -> None:
        self._path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(path))
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_DDL)

    def upsert(self, table: str, row: dict, keys: list[str]) -> None:
        columns = list(row.keys())
        placeholders = ", ".join("?" for _ in columns)
        col_list = ", ".join(columns)
        update_cols = [c for c in columns if c not in keys]
        update_clause = ", ".join(f"{c} = excluded.{c}" for c in update_cols)

        sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
        if update_clause:
            sql += f" ON CONFLICT ({', '.join(keys)}) DO UPDATE SET {update_clause}"
        else:
            sql += f" ON CONFLICT ({', '.join(keys)}) DO NOTHING"

        self._conn.execute(sql, list(row.values()))
        self._conn.commit()

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        cursor = self._conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
