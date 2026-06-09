#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Optional


def main() -> int:
    parser = argparse.ArgumentParser(description="Call the AIPE Device Intelligence API.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    search = subcommands.add_parser("search", help="Search devices.")
    search.add_argument("--q")
    search.add_argument("--type", dest="device_type")
    search.add_argument("--manufacturer")
    search.add_argument("--min-voltage", type=float)
    search.add_argument("--min-current", type=float)

    detail = subcommands.add_parser("detail", help="Read one device.")
    detail.add_argument("device_id")

    compare = subcommands.add_parser("compare", help="Compare devices.")
    compare.add_argument("device_ids", nargs="+")

    models = subcommands.add_parser("models", help="List model assets for a device.")
    models.add_argument("device_id")

    args = parser.parse_args()
    client = AipeClient()

    if args.command == "search":
        payload = client.get(
            "/api/devices",
            {
                "q": args.q,
                "type": args.device_type,
                "manufacturer": args.manufacturer,
                "min_voltage": args.min_voltage,
                "min_current": args.min_current,
            },
        )
    elif args.command == "detail":
        payload = client.get(f"/api/devices/{args.device_id}")
    elif args.command == "compare":
        payload = client.post("/api/devices/compare", {"device_ids": args.device_ids})
    elif args.command == "models":
        payload = client.get(f"/api/devices/{args.device_id}/model-assets")
    else:  # pragma: no cover
        parser.error(f"Unknown command {args.command}")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


class AipeClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.getenv("AIPE_API_BASE") or "http://127.0.0.1:8000").rstrip("/")
        self.api_key = os.getenv("AIPE_API_KEY")

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        query = urllib.parse.urlencode({key: value for key, value in (params or {}).items() if value is not None})
        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{query}"
        return self.request("GET", url)

    def post(self, path: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", f"{self.base_url}{path}", payload)

    def request(self, method: str, url: str, payload: Optional[dict[str, Any]] = None) -> Any:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["X-AIPE-API-Key"] = self.api_key
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            message = exc.read().decode("utf-8")
            raise SystemExit(f"AIPE API error {exc.code}: {message}") from exc
        except urllib.error.URLError as exc:
            raise SystemExit(f"Could not reach AIPE API at {self.base_url}: {exc}") from exc


if __name__ == "__main__":
    sys.exit(main())
