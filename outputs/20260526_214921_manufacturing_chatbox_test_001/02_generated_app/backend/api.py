"""Local API and static frontend server."""

from __future__ import annotations

import errno
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from backend.agent import run_case, run_interaction
from backend.data_store import load_product_spec, load_sample_cases
from backend.llm_client import connection_status


APP_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = APP_DIR / "frontend"


class ProductHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: object, status: int = 200) -> None:
        self._send_bytes(json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"), "application/json; charset=utf-8", status)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path in {"/", "/index.html"}:
            self._send_bytes((FRONTEND_DIR / "index.html").read_bytes(), "text/html; charset=utf-8")
            return
        if parsed.path == "/frontend/styles.css":
            self._send_bytes((FRONTEND_DIR / "styles.css").read_bytes(), "text/css; charset=utf-8")
            return
        if parsed.path == "/frontend/app.js":
            self._send_bytes((FRONTEND_DIR / "app.js").read_bytes(), "application/javascript; charset=utf-8")
            return
        if parsed.path == "/frontend/generated_ui_config.json":
            self._send_bytes((FRONTEND_DIR / "generated_ui_config.json").read_bytes(), "application/json; charset=utf-8")
            return
        if parsed.path == "/frontend/generated_interaction_config.json":
            self._send_bytes((FRONTEND_DIR / "generated_interaction_config.json").read_bytes(), "application/json; charset=utf-8")
            return
        if parsed.path == "/frontend/generated_layout_config.json":
            self._send_bytes((FRONTEND_DIR / "generated_layout_config.json").read_bytes(), "application/json; charset=utf-8")
            return
        if parsed.path == "/pipeline_diagram.svg":
            self._send_bytes((APP_DIR / "pipeline_diagram.svg").read_bytes(), "image/svg+xml; charset=utf-8")
            return
        if parsed.path == "/analysis_charts.svg":
            self._send_bytes((APP_DIR / "analysis_charts.svg").read_bytes(), "image/svg+xml; charset=utf-8")
            return
        if parsed.path == "/api/product_readiness":
            self._send_json(json.loads((APP_DIR / "product_readiness.json").read_text(encoding="utf-8")))
            return
        if parsed.path == "/api/product_spec":
            self._send_json(load_product_spec())
            return
        if parsed.path in {"/api/runtime_status", "/api/status"}:
            self._send_json(connection_status())
            return
        if parsed.path == "/api/app_design":
            self._send_json(json.loads((APP_DIR / "llm_app_design.json").read_text(encoding="utf-8")))
            return
        if parsed.path == "/api/interaction_config":
            self._send_json(json.loads((FRONTEND_DIR / "generated_interaction_config.json").read_text(encoding="utf-8")))
            return
        if parsed.path == "/api/layout_config":
            self._send_json(json.loads((FRONTEND_DIR / "generated_layout_config.json").read_text(encoding="utf-8")))
            return
        if parsed.path == "/api/sample_cases":
            self._send_json(load_sample_cases())
            return
        self._send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/recommend", "/api/assistant"}:
            self._send_json({"error": "not found"}, 404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw or "{}")
            if parsed.path == "/api/assistant":
                self._send_json(run_interaction(payload))
            else:
                self._send_json(run_case(payload))
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": str(exc)}, 500)

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        print(f"[generated_product] {self.address_string()} - {format % args}")


def serve(port: int = 8766) -> None:
    for candidate_port in range(port, port + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate_port), ProductHandler)
            print(f"Generated product running at http://127.0.0.1:{candidate_port}")
            server.serve_forever()
            return
        except OSError as error:
            if error.errno != errno.EADDRINUSE:
                raise
            print(f"Port {candidate_port} is already in use; trying {candidate_port + 1}...")
    raise OSError(f"No available local port found in range {port}-{port + 19}")
