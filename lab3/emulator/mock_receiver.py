import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API_KEY = os.environ.get("MOCK_API_KEY", "local-key")
SENSOR_TYPES = {"temperature", "humidity", "light", "camera"}
REQUIRED = ("sensor_id", "sensor_type", "value", "unit", "location", "measured_at")
counters = {"accepted": 0, "rejected": 0, "images": 0}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def _send(self, status, body=None):
        payload = json.dumps(body).encode() if body is not None else b""
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _body(self):
        return self.rfile.read(int(self.headers.get("content-length", 0)))

    def do_PUT(self):
        if self.path.startswith("/upload/"):
            self._body()
            counters["images"] += 1
            return self._send(200)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.headers.get("x-api-key") != API_KEY:
            return self._send(401, {"error": "invalid or missing x-api-key"})
        raw = self._body()
        try:
            data = json.loads(raw)
        except ValueError:
            counters["rejected"] += 1
            return self._send(400, {"error": "invalid JSON body"})

        if self.path == "/ingest":
            missing = [f for f in REQUIRED if f not in data]
            if missing or data.get("sensor_type") not in SENSOR_TYPES:
                counters["rejected"] += 1
                return self._send(400, {"error": "validation failed", "details": missing})
            counters["accepted"] += 1
            if counters["accepted"] % 500 == 0:
                print(f"accepted={counters['accepted']} rejected={counters['rejected']} images={counters['images']}",
                      flush=True)
            return self._send(202, {"message_id": str(uuid.uuid4())})

        if self.path == "/camera/upload-url":
            key = f"camera/{data.get('sensor_id')}/{uuid.uuid4()}.png"
            host = self.headers.get("host", "localhost:8080")
            return self._send(200, {"upload_url": f"http://{host}/upload/{key}", "object_key": key,
                                    "content_type": "image/png", "expires_in": 600})
        self._send(404, {"error": "not found"})


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"Mock receiver on http://localhost:{port}, api key: {API_KEY}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
