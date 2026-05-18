from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .csv_import import parse_curve_csv
from .index import DeviceIndex
from .repository import DeviceRepository
from .taxonomy import TAXONOMY
from .validation import validate_device_record


app = FastAPI(title="AIPE Power Device Library", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

repository = DeviceRepository()
index = DeviceIndex()


@app.on_event("startup")
def startup() -> None:
    index.rebuild(repository)


@app.get("/api/devices")
def list_devices(
    q: Optional[str] = None,
    manufacturer: Optional[str] = None,
    technology: Optional[str] = None,
    device_class: Optional[str] = None,
    min_voltage: Optional[float] = Query(default=None),
    min_current: Optional[float] = Query(default=None),
) -> list[dict[str, Any]]:
    rows = index.search(
        {
            "q": q,
            "manufacturer": manufacturer,
            "technology": technology,
            "device_class": device_class,
            "min_voltage": min_voltage,
            "min_current": min_current,
        }
    )
    return rows


@app.get("/api/devices/{device_id}")
def get_device(device_id: str) -> dict[str, Any]:
    try:
        record = repository.load(device_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device not found") from exc
    validation = validate_device_record(record)
    return {"device": record, "validation": validation}


@app.post("/api/devices")
def create_device(record: dict[str, Any]) -> dict[str, Any]:
    validation = validate_device_record(record)
    if validation["errors"]:
        raise HTTPException(status_code=422, detail=validation)
    path = repository.save(record)
    index.rebuild(repository)
    return {"device": record, "file": path.name, "validation": validation}


@app.put("/api/devices/{device_id}")
def update_device(device_id: str, record: dict[str, Any]) -> dict[str, Any]:
    record["id"] = device_id
    validation = validate_device_record(record)
    if validation["errors"]:
        raise HTTPException(status_code=422, detail=validation)
    path = repository.save(record)
    index.rebuild(repository)
    return {"device": record, "file": path.name, "validation": validation}


@app.post("/api/devices/validate")
def validate_device(record: dict[str, Any]) -> dict[str, list[str]]:
    return validate_device_record(record)


@app.post("/api/index/rebuild")
def rebuild_index() -> dict[str, int]:
    return index.rebuild(repository)


@app.get("/api/taxonomy")
def get_taxonomy() -> dict[str, list[str]]:
    return TAXONOMY


@app.post("/api/curves/import-csv")
def import_curve_csv(payload: dict[str, Any]) -> dict[str, Any]:
    required = [
        "csv_text",
        "curve_id",
        "curve_type",
        "x_label",
        "x_unit",
        "y_label",
        "y_unit",
        "source_id",
    ]
    missing = [key for key in required if key not in payload]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing fields: {missing}")
    curve = parse_curve_csv(
        payload["csv_text"],
        curve_id=payload["curve_id"],
        curve_type=payload["curve_type"],
        x_label=payload["x_label"],
        x_unit=payload["x_unit"],
        y_label=payload["y_label"],
        y_unit=payload["y_unit"],
        source_id=payload["source_id"],
        condition=payload.get("condition"),
    )
    return {"curve": curve, "points": len(curve["points"])}
