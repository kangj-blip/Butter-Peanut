import csv
import json

import sys
import os

BASE_DIR = os.path.join(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.join(BASE_DIR, "app")
DRAWS_DIR = os.path.join(APP_DIR, "draws")
PARTICIPANTS_DIR = os.path.join(APP_DIR, "participants")

ROOMS_FILE = os.path.join(APP_DIR, "rooms.csv")
DRAWS_FILE = os.path.join(DRAWS_DIR, "draws.json")
UNSLOTTED_FILE = os.path.join(DRAWS_DIR, "unSlotted.json")
PARTICIPANTS_FILE = os.path.join(PARTICIPANTS_DIR, "participants.json")

from participants.participants import Team, Judge

class Room:
	def __init__(self, roomnum, OG, OO, CG, CO):
		self.roomnum = roomnum
		self.OG = OG
		self.OO = OO
		self.CG = CG
		self.CO = CO
		#self.judges = judges # [string, string, string, ...]

	def __str__(self):
		return (
			f"{self.roomnum}\n"
			f"OG: {self.OG}\n"
			f"OO: {self.OO}\n"
			f"CG: {self.CG}\n"
			f"CO: {self.CO}\n"
		)

	def to_dict(self):
		return {
			"Room": self.roomnum,
			"OG": self.OG.debaters if self.OG != "unslotted" else "",
			"OO": self.OO.debaters if self.OO != "unslotted" else "",
			"CG": self.CG.debaters if self.CG != "unslotted" else "",
			"CO": self.CO.debaters if self.CO != "unslotted" else ""
		}

	@staticmethod
	def importRooms():
		with open(ROOMS_FILE, newline="", encoding="utf-8") as file:
			reader = csv.DictReader(file)
			rooms = list(reader)

		return rooms

	@staticmethod
	def makeRooms():

		with open(UNSLOTTED_FILE, "w", encoding="utf-8") as file:
			json.dump([], file)
			
		rooms = Room.importRooms()
		teams = Team.makeTeams()
		judges = Judge.getJudges()

		slottedTeams = set()
		slottedRooms = []

		OGTeams = Team.findTeamsForPosition(teams, "OG")
		OOTeams = Team.findTeamsForPosition(teams, "OO")
		CGTeams = Team.findTeamsForPosition(teams, "CG")
		COTeams = Team.findTeamsForPosition(teams, "CO")

		i = 0
		for room in rooms:

			roomnum = room["roomnum"]

			if i < len(OGTeams):
				if OGTeams[i] not in slottedTeams:
					OG = OGTeams[i]
					slottedTeams.add(OGTeams[i])
				else:
					OG = "unslotted"
			else:
				OG = "unslotted"


			if i < len(OOTeams):
				if OOTeams[i] not in slottedTeams:
					OO = OOTeams[i]
					slottedTeams.add(OOTeams[i])
				else:
					OO = "unslotted"
			else:
				OO = "unslotted"


			if i < len(CGTeams):
				if CGTeams[i] not in slottedTeams:
					CG = CGTeams[i]
					slottedTeams.add(CGTeams[i])
				else:
					CG = "unslotted"
			else:
				CG = "unslotted"


			if i < len(COTeams):
				if COTeams[i] not in slottedTeams:
					CO = COTeams[i]
					slottedTeams.add(COTeams[i])
				else:
					CO = "unslotted"
			else:
				CO = "unslotted"


			newRoom = Room(roomnum = roomnum, OG = OG, OO = OO, CG = CG, CO = CO)

			i = i+1
			slottedRooms.append(newRoom)


		with open(DRAWS_FILE, "w") as f:
			json.dump([room.to_dict() for room in slottedRooms], f, indent=4)

		unSlotted = []
		for team in teams:
			if team not in slottedTeams:
				unSlotted.append(team)
		with open(UNSLOTTED_FILE, "w") as f:
			json.dump([team.to_dict() for team in unSlotted], f, indent=4)

		Room.checkDraws()
		return slottedRooms

	@staticmethod
	def checkDraws():
		with open(PARTICIPANTS_FILE, encoding="utf-8") as f:
			participants = json.load(f)

		with open(DRAWS_FILE, encoding="utf-8") as file:
			draws = json.load(file)

		print("Checking Scratches.")
		conflicts = []

		for room in draws:
			speakers = sum(
				[
					room[pos]
					for pos in ["OG", "OO", "CG", "CO"]
					if isinstance(room[pos], list)
				],
				[]
			)

			for speaker in speakers:
				for speakerSearch in participants:
					if speakerSearch["name"] == speaker:
						for scratchSearch in speakers:
							if scratchSearch in speakerSearch["scratches"]:
								message = (
									f"Scratch conflict in {room['Room']}: "
									f"{speaker} scratches {scratchSearch}"
								)

								print(message)

								conflicts.append({
									"room": room["Room"],
									"speaker": speaker,
									"scratch": scratchSearch,
									"message": message
								})

		return conflicts

	@staticmethod
	def checkDrawsPosition():
		with open(PARTICIPANTS_FILE, encoding="utf-8") as f:
			participants = json.load(f)

		with open(DRAWS_FILE, encoding="utf-8") as file:
			draws = json.load(file)

		print("Checking Positions.")
		positionConflicts = []

		for room in draws:
			speakers = [
				(speaker, pos)
				for pos in ["OG", "OO", "CG", "CO"]
				if isinstance(room[pos], list)
				for speaker in room[pos]
			]

			for speaker,position in speakers:
				for speakerSearch in participants:
					if speakerSearch["name"] == speaker:
						if speakerSearch["positions"]:
							if position not in speakerSearch["positions"]:
								message = (
									f"Position conflict in {room['Room']}: "
									f"{speaker} wants {', '.join(speakerSearch['positions'])}"
								)

								print(message)

								positionConflicts.append({
									"room": room["Room"],
									"speaker": speaker,
									"position": position,
									"message": message
								})

		return positionConflicts