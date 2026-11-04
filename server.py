"""Chart service: the open-source (AGPL-3.0) part of the workbench.

Runs the chart engine (八字 / 紫微 via the bundled Node engine, 印占 via
Swiss Ephemeris) and the Vedic transit table as a small HTTP service. The
paid analysis app calls it over HTTP and never loads this code, so the two
are separate programs.

Endpoints (JSON):
  GET  /v1/health              engine availability
  GET  /v1/source              where the complete source of this service is published
  POST /v1/charts              chart_input -> full chart (same output as charts.calculate)
  POST /v1/normalize           raw input -> normalized chart_input
  POST /v1/transits            {"chart_input": ...} -> {"section": transit table text}

Errors: 400 {"error", "field"} for invalid birth data; 503 for engine problems.

Environment:
  CHART_PORT=8095              listens on 127.0.0.1 only
  CHART_SERVICE_TOKEN=...      optional shared secret, sent as X-Chart-Token
  CHART_SOURCE_URL=https://... where this service's source is published (AGPL §13)

Run:  python -X utf8 chart_service/server.py
"""

from __future__ import annotations

import hmac
import json
import os
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
# In the workbench repository the engine lives under app/; in the exported
# package it sits next to this file. Either layout works.
for folder in (HERE / "engine", HERE, HERE.parent / "app" / "engine", HERE.parent / "app"):
    if folder.is_dir() and str(folder) not in sys.path:
        sys.path.insert(0, str(folder))

import charts        # noqa: E402
import transits      # noqa: E402

BODY_LIMIT = 131072
VERSION = "1"


def token() -> str:
    return os.environ.get("CHART_SERVICE_TOKEN", "").strip()


class Handler(BaseHTTPRequestHandler):
    server_version = "ChartService/" + VERSION
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{datetime.now():%H:%M:%S}] {fmt % args}", flush=True)

    def send_json(self, status: int, value: object) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def allowed(self) -> bool:
        expected = token()
        if expected and not hmac.compare_digest(expected.encode(), (self.headers.get("X-Chart-Token") or "").encode()):
            self.close_connection = True
            self.send_json(403, {"error": "chart service token required"})
            return False
        return True

    def do_GET(self) -> None:
        if not self.allowed():
            return
        path = urlsplit(self.path).path
        if path == "/v1/health":
            self.send_json(200, {"ok": True, "service": "chart-service", "version": VERSION, **charts.health()})
        elif path == "/v1/source":
            self.send_json(200, {"license": "AGPL-3.0-only",
                                 "source": os.environ.get("CHART_SOURCE_URL", "")})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if not self.allowed():
            return
        path = urlsplit(self.path).path
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if not 0 < length <= BODY_LIMIT:
            self.close_connection = True
            self.send_json(413, {"error": "排盘请求大小无效。"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {"error": "请求数据不是有效 JSON"})
            return
        if not isinstance(payload, dict):
            self.send_json(400, {"error": "请求必须是 JSON 对象。"})
            return
        try:
            if path == "/v1/charts":
                self.send_json(200, charts.calculate(payload))
            elif path == "/v1/normalize":
                self.send_json(200, charts.normalize_input(payload))
            elif path == "/v1/transits":
                chart = charts.calculate(payload.get("chart_input"))
                self.send_json(200, {"section": transits.template_section(chart)})
            else:
                self.send_json(404, {"error": "not found"})
        except charts.ChartInputError as exc:
            self.send_json(400, {"error": str(exc), "field": getattr(exc, "field", "")})
        except RuntimeError as exc:
            self.send_json(503, {"error": str(exc)[:600]})


def main() -> None:
    port = int(os.environ.get("CHART_PORT", "8095"))
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"chart service (AGPL-3.0): http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
