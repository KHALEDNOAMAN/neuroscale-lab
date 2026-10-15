from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con


def initialize(path: str | Path) -> None:
    con = connect(path)
    schema = Path(__file__).with_name("schema.sql").read_text()
    con.executescript(schema)
    con.commit(); con.close()


def register_demo(con: sqlite3.Connection) -> int:
    con.execute("INSERT OR IGNORE INTO dataset(name,version,doi,license) VALUES (?,?,?,?)", ("NeuroScale synthetic demo", "0.1", None, "synthetic-fixture"))
    return int(con.execute("SELECT dataset_id FROM dataset WHERE name=?", ("NeuroScale synthetic demo",)).fetchone()[0])
