---
name: aipe-power-device
description: Use when selecting, comparing, inspecting, or checking model assets for power semiconductor devices through the AIPE Device Intelligence API.
---

# AIPE Power Device

Use this skill when a user asks Codex to search power semiconductors, compare
candidate devices, inspect a device record, or check whether simulation model
assets exist.

## Rules

- Use the AIPE API through `scripts/aipe.py`; do not invent device parameters.
- Default API base is `http://127.0.0.1:8000`; override with `AIPE_API_BASE`.
- If `AIPE_API_KEY` is set, the script sends it as `X-AIPE-API-Key`.
- Explain that V1 model assets are an index only. Do not claim PLECS, SPICE,
  Matlab, or Simulink models are validated unless the API says so.
- Always mention source/provenance when available, especially TDB public sample
  and datasheet links.

## Commands

Search:

```bash
python scripts/aipe.py search --q "GaN" --min-voltage 650
```

Detail:

```bash
python scripts/aipe.py detail gansystems-gs66506t
```

Compare:

```bash
python scripts/aipe.py compare gansystems-gs66506t cree-c3m0016120k
```

Model assets:

```bash
python scripts/aipe.py models gansystems-gs66506t
```
