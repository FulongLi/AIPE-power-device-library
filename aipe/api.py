from __future__ import annotations

from typing import Any, Optional

from fastapi import Body, Depends, FastAPI, HTTPException, Query

from . import __version__
from .auth import verify_api_key
from .importer import import_aipe_pdl_seeds
from .repository import DeviceRepository


app = FastAPI(title="AIPE Device Intelligence", version=__version__)
repository = DeviceRepository()


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": __version__,
        "device_count": len(repository.list_devices()),
        "platform": "AIPE PDL",
    }


@app.get("/api/devices", dependencies=[Depends(verify_api_key)])
def list_devices(
    q: Optional[str] = None,
    device_type: Optional[str] = Query(default=None, alias="type"),
    manufacturer: Optional[str] = None,
    min_voltage: Optional[float] = None,
    min_current: Optional[float] = None,
) -> list[dict[str, Any]]:
    return repository.search_devices(
        q=q,
        device_type=device_type,
        manufacturer=manufacturer,
        min_voltage=min_voltage,
        min_current=min_current,
    )


@app.get("/api/devices/{device_id}", dependencies=[Depends(verify_api_key)])
def get_device(device_id: str) -> dict[str, Any]:
    try:
        return repository.load_device(device_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device not found") from exc


@app.post("/api/devices/compare", dependencies=[Depends(verify_api_key)])
def compare_devices(payload: dict[str, Any]) -> dict[str, Any]:
    device_ids = payload.get("device_ids")
    if not isinstance(device_ids, list) or not all(isinstance(item, str) for item in device_ids):
        raise HTTPException(status_code=422, detail="device_ids must be a list of strings.")
    return repository.compare_devices(device_ids)


@app.get("/api/devices/{device_id}/model-assets", dependencies=[Depends(verify_api_key)])
def model_assets(device_id: str) -> list[dict[str, Any]]:
    try:
        return repository.list_model_assets(device_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device not found") from exc


@app.post("/api/admin/import-aipe-pdl-seeds", dependencies=[Depends(verify_api_key)])
def import_native_aipe_pdl_seeds(payload: Optional[dict[str, Any]] = Body(default=None)) -> dict[str, Any]:
    return import_aipe_pdl_seeds(repository=repository)
