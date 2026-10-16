from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import sys
import traceback
from urllib.parse import urlparse

# ==================================================
# PATHS
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")
DRAWS_DIR = os.path.join(APP_DIR, "draws")
MOTIONS_DIR = os.path.join(APP_DIR, "motions")
PARTICIPANTS_DIR = os.path.join(APP_DIR, "participants")

DRAWS_FILE = os.path.join(DRAWS_DIR, "draws.json")
UNSLOTTED_FILE = os.path.join(DRAWS_DIR, "unSlotted.json")
MOTIONS_FILE = os.path.join(MOTIONS_DIR, "motions.json")
PARTICIPANTS_FILE = os.path.join(PARTICIPANTS_DIR, "participants.json")

HHDC_LOGO_JPG = os.path.join(APP_DIR, "hhdclogo.jpg")

MAIN_HTML_FILE = os.path.join(APP_DIR, "main.html")
DRAWS_HTML_FILE = os.path.join(DRAWS_DIR, "draws.html")
MOTIONS_HTML_FILE = os.path.join(MOTIONS_DIR, "motions.html")
PARTICIPANTS_HTML_FILE = os.path.join(PARTICIPANTS_DIR, "participantsImport.html")

sys.path.insert(0, APP_DIR)

from participants.participants import Participants, Team, Judge
from draws.slotting import Room

def read_draw():
	if not os.path.exists(DRAWS_FILE):
		return []

	with open(DRAWS_FILE, "r", encoding="utf-8") as file:
		return json.load(file)


def saveDraws(draw):
	with open(DRAWS_FILE, "w", encoding="utf-8") as file:
		json.dump(draw, file, indent=4, ensure_ascii=False)


# ==================================================
# HTTP REQUEST HANDLER
# ==================================================

class RequestHandler(BaseHTTPRequestHandler):

	def send_json(self, data, status=200):
		response = json.dumps(
			data,
			ensure_ascii=False
		).encode("utf-8")

		self.send_response(status)
		self.send_header(
			"Content-Type",
			"application/json; charset=utf-8"
		)
		self.send_header("Content-Length", str(len(response)))
		self.send_header("Cache-Control", "no-store")
		self.end_headers()

		self.wfile.write(response)

	def send_file(self, filepath, content_type):
		if not os.path.isfile(filepath):
			self.send_error(404, "File not found")
			return

		with open(filepath, "rb") as file:
			content = file.read()

		self.send_response(200)
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", str(len(content)))
		self.send_header("Cache-Control", "no-store")
		self.end_headers()

		self.wfile.write(content)

	def content_type_for(self, filename):
		if filename.endswith(".css"):
			return "text/css; charset=utf-8"

		elif filename.endswith(".js"):
			return "application/javascript; charset=utf-8"

		elif filename.endswith(".json"):
			return "application/json; charset=utf-8"

		elif filename.endswith(".jpg"):
			return "image/jpeg"

		return "application/octet-stream"

	def read_request_body(self):

		content_length = int(
			self.headers.get("Content-Length", "0")
		)

		if content_length > 2_000_000:
			raise ValueError("Request body is too large.")

		body = self.rfile.read(content_length)

		if not body:
			return None

		return json.loads(body.decode("utf-8"))

	# ==================================================
	# GET REQUESTS
	# ==================================================

	def do_GET(self):
		path = urlparse(self.path).path
		print(f"GET {path}")

		if path == "/" or path == "/main.html":
			self.send_file(MAIN_HTML_FILE, "text/html; charset=utf-8")
			return
			
		elif path == "/draws.html":
			self.send_file(DRAWS_HTML_FILE, "text/html; charset=utf-8")
			return

		elif path == "/motions.html":
			self.send_file(MOTIONS_HTML_FILE, "text/html; charset=utf-8")
			return

		elif path == "/participantsImport.html":
			self.send_file(PARTICIPANTS_HTML_FILE, "text/html; charset=utf-8")

		elif path == "/api/draw":
			try:
				self.send_json(read_draw())
			except Exception as error:
				self.send_json({"error": str(error)}, 500)
			return

		elif path == "/draws.json":
			self.send_file(DRAWS_FILE, "application/json; charset=utf-8")
			return

		elif path == "/unSlotted.json":
			self.send_file(UNSLOTTED_FILE, "application/json; charset=utf-8")
			return

		elif path == "/motions.json":
			self.send_file(MOTIONS_FILE, "application/json; charset=utf-8")
			return

		elif path == "/hhdclogo.jpg":
			self.send_file(HHDC_LOGO_JPG, "image/jpeg")
			return

		elif path.endswith((".css", ".js")):
			filename = os.path.basename(path)
			app_file = os.path.join(APP_DIR, filename)
			draws_file = os.path.join(DRAWS_DIR, filename)
			motions_file = os.path.join(MOTIONS_DIR, filename)
			participants_file = os.path.join(PARTICIPANTS_DIR, filename)

			if os.path.isfile(app_file):
				self.send_file(app_file, self.content_type_for(filename))

			elif os.path.isfile(draws_file):
				self.send_file(draws_file, self.content_type_for(filename))

			elif os.path.isfile(motions_file):
				self.send_file(motions_file, self.content_type_for(filename))

			elif os.path.isfile(participants_file):
				self.send_file(participants_file, self.content_type_for(filename))

			else:
				self.send_error(404, "Static file not found")

			return

		self.send_error(404, "Not found")


	# ==================================================
	# POST REQUESTS
	# ==================================================

	def do_POST(self):
		path = urlparse(self.path).path

		print(f"POST {path}")


		if path == "/api/generate-draw":
			try:
				Participants.importParticipants()
				Room.makeRooms()

				generated_draw = read_draw()

				with open(UNSLOTTED_FILE, "r", encoding="utf-8") as file:
					generated_unslotted = json.load(file)

				self.send_json({
					"success": True,
					"draw": generated_draw,
					"unslotted": generated_unslotted
				})

			except Exception as error:
				traceback.print_exc()
				self.send_json({"error": str(error)}, 500)

			return

		if path == "/api/draw":
			try:
				draw = self.read_request_body()

				if not isinstance(draw, list):
					self.send_json({"error": "Draw must be a list of rooms."}, 400)
					return

				saveDraws(draw)
				conflicts = Room.checkDraws()
				positionConflicts = Room.checkDrawsPosition()

				self.send_json({
					"success": True,
					"conflicts": conflicts,
					"positionConflicts": positionConflicts
				})


			except Exception as error:
				traceback.print_exc()
				self.send_json({"error": str(error)}, 500)

			return

		if path == "/api/unSlotted":
			try:
				teams = self.read_request_body()

				if not isinstance(teams, list):
					self.send_json({
						"error": "Unslotted teams must be a list."
					}, 400)
					return

				with open(UNSLOTTED_FILE, "w", encoding="utf-8") as file:
					json.dump(teams, file, indent=4, ensure_ascii=False)

				self.send_json({"success": True})

			except Exception as error:
				traceback.print_exc()
				self.send_json({"error": str(error)}, 500)

			return

		if path in ("/api/import-csv/signups", "/api/import-csv/rooms"):
			try:
				content_length = int(
					self.headers.get("Content-Length", "0")
				)

				if content_length <= 0 or content_length > 5_000_000:
					self.send_json(
						{"error": "CSV file is empty or too large."},
						400
					)
					return

				csv_content = self.rfile.read(
					content_length
				).decode("utf-8-sig")

				if not csv_content.strip():
					self.send_json(
						{"error": "CSV file is empty."},
						400
					)
					return

				target_file = (
					os.path.join(APP_DIR, "signups.csv")
					if path.endswith("/signups")
					else os.path.join(APP_DIR, "rooms.csv")
				)

				# Validate the CSV before replacing the existing file.
				import io
				import csv

				reader = csv.reader(io.StringIO(csv_content))
				rows = list(reader)

				if len(rows) < 2 or not any(cell.strip() for cell in rows[0]):
					self.send_json(
						{"error": "CSV must contain a header and at least one data row."},
						400
					)
					return

				with open(target_file, "w", encoding="utf-8", newline="") as file:
					file.write(csv_content)

				self.send_json({"success": True})

			except Exception as error:
				traceback.print_exc()
				self.send_json({"error": str(error)}, 500)

			return
		

		self.send_error(404, "Not found")




# ==================================================
# START SERVER
# ==================================================

HOST = "127.0.0.1"
PORT = 8000

server = HTTPServer((HOST, PORT), RequestHandler)

print()
print("===================================")
print("	   BUTTER PEANUT TAB")
print("===================================")
print(f"Website: http://localhost:{PORT}")
print("Press Ctrl+C to stop the server.")
print()

try:
	server.serve_forever()
except KeyboardInterrupt:
	print("\nShutting down server...")
finally:
	server.server_close()
