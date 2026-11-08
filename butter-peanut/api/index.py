from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = {
            "success": True,
            "message": "Butter Peanut API is running!",
            "blob_connected": bool(
                os.environ.get("NUT_READ_WRITE_TOKEN")
                or (
                    os.environ.get("VERCEL_OIDC_TOKEN")
                    and os.environ.get("NUT_STORE_ID")
                )
            )
        }

        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
