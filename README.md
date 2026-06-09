# AIPE PDL Device Intelligence V1

AIPE PDL V1 is a Codex-facing gateway for AIPE Power Device Library records and
model asset discovery. It imports native AIPE PDL seed records, stores
normalized device summaries, and exposes a small FastAPI surface that a Codex
skill can call for search, detail, comparison, and model-asset lookup.

V1 intentionally has no frontend and does not generate PLECS, SPICE, Matlab, or
Simulink models. It only records available model/data assets so later exporters
can be added without changing the agent workflow.

## Layout

```text
aipe/                    Core API, repository, AIPE PDL import, auth, comparison
data/aipe_pdl_seed/      Native AIPE PDL seed records
data/devices/            Normalized AIPE DeviceSummary JSON files
data/model_assets/       Optional manually registered model asset JSON files
skill/aipe-power-device/ Codex skill and helper script
tests/                   Offline unit/API tests
```

## Quick Start

Create an environment and install the API dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Import the native AIPE PDL seed records into normalized device summaries:

```bash
python -c "from aipe.importer import import_aipe_pdl_seeds; from aipe.repository import DeviceRepository; print(import_aipe_pdl_seeds(repository=DeviceRepository()))"
```

Start the local API:

```bash
uvicorn aipe.api:app --reload
```

The API serves `http://127.0.0.1:8000/api`.

Check that it is running:

```bash
curl http://127.0.0.1:8000/api/health
```

## Usage Examples

Search AIPE PDL devices:

```bash
curl "http://127.0.0.1:8000/api/devices?min_voltage=650"
```

Read one device:

```bash
curl http://127.0.0.1:8000/api/devices/aipe-pdl-gan650-ref
```

Compare candidate devices:

```bash
curl -X POST http://127.0.0.1:8000/api/devices/compare \
  -H "Content-Type: application/json" \
  -d '{"device_ids":["aipe-pdl-gan650-ref","aipe-pdl-sic1200-ref"]}'
```

List model assets for a device:

```bash
curl http://127.0.0.1:8000/api/devices/aipe-pdl-gan650-ref/model-assets
```

Use the Codex helper script:

```bash
python skill/aipe-power-device/scripts/aipe.py search --q GaN
python skill/aipe-power-device/scripts/aipe.py compare aipe-pdl-gan650-ref aipe-pdl-sic1200-ref
```

## API

- `GET /api/health`
- `GET /api/devices?q=&type=&manufacturer=&min_voltage=&min_current=`
- `GET /api/devices/{device_id}`
- `POST /api/devices/compare`
- `GET /api/devices/{device_id}/model-assets`
- `POST /api/admin/import-aipe-pdl-seeds`

## Auth

Local development is open by default. Set both values below to require API-key
auth:

```bash
export AIPE_REQUIRE_API_KEY=1
export AIPE_API_KEY=your-token
```

Requests must then include `X-AIPE-API-Key`.

## Tests

Run the offline test suite:

```bash
.venv/bin/python -m unittest discover -s tests
```

## Model Asset Note

V1 records model asset availability and planned model slots. It does not claim
SPICE, PLECS, Matlab, or Simulink models are validated unless an AIPE PDL asset
record explicitly marks them available.
