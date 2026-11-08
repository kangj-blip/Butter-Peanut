from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        store_id = (
            os.environ.get("NUT_STORE_ID")
        )

        read_write_token = os.environ.get(
            "BLOB_READ_WRITE_TOKEN"
        )

        oidc_header = self.headers.get(
            "x-vercel-oidc-token"
        )

        response = {
            "success": True,
            "message": "Butter Peanut API is running!",
            "store_id_configured": bool(store_id),
            "read_write_token_configured": bool(read_write_token),
            "oidc_header_received": bool(oidc_header)
        }

        body = json.dumps(response).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
