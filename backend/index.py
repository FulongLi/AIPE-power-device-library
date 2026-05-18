from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from .config import INDEX_PATH
from .repository import DeviceRepository


class DeviceIndex:
    def __init__(self, index_path: Path = INDEX_PATH):
        self.index_path = index_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.index_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    id TEXT PRIMARY KEY,
                    manufacturer TEXT NOT NULL,
                    part_number TEXT NOT NULL,
                    technology TEXT NOT NULL,
                    device_class TEXT NOT NULL,
                    package_name TEXT NOT NULL,
                    voltage_v REAL,
                    current_a REAL,
                    tags TEXT,
                    file_name TEXT NOT NULL
                )
                """
            )

    def rebuild(self, repository: DeviceRepository) -> dict[str, int]:
        self.initialize()
        devices = repository.list_devices()
        with self.connect() as connection:
            connection.execute("DELETE FROM devices")
            for record in devices:
                connection.execute(
                    """
                    INSERT INTO devices (
                        id, manufacturer, part_number, technology, device_class,
                        package_name, voltage_v, current_a, tags, file_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.get("id", ""),
                        record.get("manufacturer", ""),
                        record.get("part_number", ""),
                        record.get("technology", ""),
                        record.get("device_class", ""),
                        record.get("package", {}).get("name", ""),
                        _quantity_value(record, "ratings.voltage"),
                        _quantity_value(record, "ratings.current"),
                        ",".join(record.get("tags", [])),
                        record.get("_file", ""),
                    ),
                )
        return {"indexed": len(devices)}

    def search(self, filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        self.initialize()
        filters = filters or {}
        where: list[str] = []
        params: list[Any] = []
        if filters.get("q"):
            where.append("(manufacturer LIKE ? OR part_number LIKE ? OR tags LIKE ?)")
            q = f"%{filters['q']}%"
            params.extend([q, q, q])
        for key in ["technology", "device_class", "manufacturer"]:
            if filters.get(key):
                where.append(f"{key} = ?")
                params.append(filters[key])
        if filters.get("min_voltage") is not None:
            where.append("voltage_v >= ?")
            params.append(filters["min_voltage"])
        if filters.get("min_current") is not None:
            where.append("current_a >= ?")
            params.append(filters["min_current"])
        sql = "SELECT * FROM devices"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY manufacturer, part_number"
        with self.connect() as connection:
            rows = connection.execute(sql, params).fetchall()
            return [dict(row) for row in rows]


def _quantity_value(record: dict[str, Any], dotted_path: str) -> float | None:
    value: Any = record
    for part in dotted_path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    if isinstance(value, dict) and isinstance(value.get("value"), (int, float)):
        return float(value["value"])
    return None
