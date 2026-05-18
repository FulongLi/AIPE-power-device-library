# AIPE Power Device Library

Local web application and data library for managing power semiconductor devices.

The project is built around a source-of-truth file library: each device is stored
as a YAML or JSON file under `devices/`, while SQLite is used as a disposable
search index that can be rebuilt at any time.

## First-version Scope

- Device families: Si MOSFET, SiC MOSFET/JFET/SBD, GaN HEMT, IGBT, diodes, and
  power modules.
- Data integrity: every parameter and curve references a source, declares units,
  and records test conditions where available.
- Local management UI: React/Vite frontend with device list, detail views,
  comparison, validation status, and curve import preview.
- Backend API: FastAPI endpoints for listing, reading, creating, updating,
  validating, indexing, taxonomy lookup, and CSV curve import.

## Layout

```text
backend/          FastAPI app and data/index services
devices/          YAML source records, one file per device
frontend/         React/Vite management UI
schemas/          JSON Schema documentation for the device file shape
templates/        Data-entry templates for datasheet and characterization sources
tests/            Standard-library tests for validation and indexing behavior
```

## Run Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

The backend serves the API at `http://127.0.0.1:8000/api`.

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://127.0.0.1:8000` by default.

## Data Philosophy

This repository deliberately separates source data from indexes and derived
outputs. Device files are reviewable in Git, while SQLite can be rebuilt using
`POST /api/index/rebuild`. Future exporters for PLECS, LTspice, Simulink,
Matlab, CSV, and virtual datasheets should consume validated `DeviceRecord`
files rather than becoming a second source of truth.

## Source Categories

Each parameter, curve, and raw dataset points back to a `source_id`. Sources are
classified by `type`, `category`, and optional `subtype`, so manufacturer
datasheets and lab characterization data can coexist in one device record.

- `manufacturer_document`: datasheet tables, datasheet curves, application notes.
- `third_party_characterization`: external lab reports and raw test datasets.
- `internal_measurement`: in-house bench data.
- `manufacturer_model`: SPICE, PLECS, or other vendor model files.
- `simulation` and `estimate`: derived or placeholder values.

Use `templates/device-record-template.yaml`,
`templates/characterization-source-template.yaml`, and
`templates/raw-data-package-template.yaml` when adding new devices.
