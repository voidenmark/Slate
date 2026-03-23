from __future__ import annotations

import sqlite3
from pathlib import Path


def initialize_database(db_path: Path, schema_path: Path) -> None:
    """Initialize (or migrate) the Slate sqlite database from schema.sql."""

    schema_sql = schema_path.read_text(encoding="utf-8")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema_sql)
        connection.commit()
