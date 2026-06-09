# AIPE Device Intelligence V1

AIPE V1 is a Codex-facing gateway for public transistor data and model asset
discovery. It imports public records from the UPB-LEA Transistor Database File
Exchange, stores raw JSON plus normalized device summaries, and exposes a small
FastAPI surface that a Codex skill can call for search, detail, comparison, and
model-asset lookup.

V1 intentionally has no frontend and does not generate PLECS, SPICE, Matlab, or
Simulink models. It only records available model/data assets so later exporters
can be added without changing the agent workflow.

## Layout

```text
aipe/                    Core API, repository, TDB import, auth, comparison
data/tdb_raw/            Raw public TDB JSON files downloaded from File Exchange
data/devices/            Normalized AIPE DeviceSummary JSON files
data/model_assets/       Optional manually registered model asset JSON files
skill/aipe-power-device/ Codex skill and helper script
tests/                   Offline unit/API tests
```

## Run

Use Python 3.11+ for the full environment because `transistordatabase==0.5.1`
requires Python 3.11 or newer.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn aipe.api:app --reload
```

The API serves `http://127.0.0.1:8000/api`.

Import the public TDB index:

```bash
curl -X POST http://127.0.0.1:8000/api/admin/import-tdb-index
```

## API

- `GET /api/health`
- `GET /api/devices?q=&type=&manufacturer=&min_voltage=&min_current=`
- `GET /api/devices/{device_id}`
- `POST /api/devices/compare`
- `GET /api/devices/{device_id}/model-assets`
- `POST /api/admin/import-tdb-index`

## Auth

Local development is open by default. Set both values below to require API-key
auth:

```bash
export AIPE_REQUIRE_API_KEY=1
export AIPE_API_KEY=your-token
```

Requests must then include `X-AIPE-API-Key`.

## License Note

This V1 directly declares `transistordatabase==0.5.1` as a research dependency
and imports public File Exchange JSON. The upstream repository has inconsistent
license signals that should be reviewed before any commercial distribution.
