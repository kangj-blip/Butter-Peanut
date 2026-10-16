import csv
import json

import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
APP_DIR = os.path.join(BASE_DIR, "app")
PARTICIPANTS_DIR = os.path.join(APP_DIR, "participants")

SIGNUPS_FILE = os.path.join(APP_DIR, "signups.csv")
PARTICIPANTS_FILE = os.path.join(PARTICIPANTS_DIR, "participants.json")

class Team:
	def __init__(self, debaters, positions, scratches):
		self.debaters = debaters # [string,string]
		self.positions = positions
		self.scratches = scratches

	def __str__(self):
		return (
			f"{self.debaters}\n"
			f"\t\tadmin: {self.positions}, {self.scratches}"
		)

	def to_dict(self):
		return (self.debaters)



	@staticmethod
	def makeTeams():
		with open(PARTICIPANTS_FILE, mode="r") as file:
			participants = json.load(file)

			debaters = []

			for participant in participants:
				if participant["debate/judge"] == "Debate":
					debaters.append(participant)

				# Deal with Either later

			teams = []
			used = set()

			for debater in debaters:
				name = debater["name"]
				partner = debater["partner"]

				if name in used:
					continue

				if partner != "":
					positions = Team.makePositionsForTeams(debater, debaters)
					scratches = Team.makeScratchesForTeams(debater, debaters)

					teams.append(Team([name,partner], positions = positions, scratches = scratches) )

					used.add(name)
					used.add(partner)

				if partner == "":
					possiblePartners = []

					for debaterSearch in debaters:
						if debaterSearch["name"] != name:
							if debaterSearch["name"] in debater["scratches"] or debaterSearch["partner"] != "":
								continue
							else:
								possiblePartners.append(debaterSearch)

					for debaterSearch in possiblePartners:
						if debater["name"] in used:
							continue

						for position in debater["positions"]:
							if position in debaterSearch["positions"]:
								partner = debaterSearch["name"]
								debater["partner"] = debaterSearch["name"]

								positions = Team.makePositionsForTeams(debater, debaters)
								scratches = Team.makeScratchesForTeams(debater, debaters)

								teams.append(Team([name,partner], positions = positions, scratches = scratches) )

								used.add(name)
								used.add(partner)

		print("Teams Made.")

		for team in teams:
			print(team)

		print("Number of Teams:", len(teams), "\n")
		return teams


	def makePositionsForTeams(debater, debaters):
		name = debater["name"]
		partner = debater["partner"]
		positions = []

		positions.append(debater["positions"])
		for search in debaters:
			if search["name"] == partner:
				positions.append(search["positions"])

		return positions

	def makeScratchesForTeams(debater, debaters):
		name = debater["name"]
		partner = debater["partner"]
		scratches = []

		scratches.append(debater["scratches"])
		for search in debaters:
			if search["name"] == partner:
				scratches.append(search["scratches"])

		return scratches



	def findTeamsForPosition(teams, slot):
		teamsForSlot = []

		for team in teams:
			for speakerPref in team.positions:
				for position in speakerPref:

					if position == slot:
						teamsForSlot.append(team)

		return teamsForSlot




class Participants:

	# All debater information must be downloaded as a .csv file and uploaded as signups.csv into the app folder
	# Name, Debate/Judge/Either, Pro/Nov, Partner, Positions, Scratches

	@staticmethod
	def importParticipants():
		with open(SIGNUPS_FILE, newline="", encoding="utf-8") as file:
			reader = csv.DictReader(file)
			signups = list(reader)

			for signup in signups:
				signup["positions"] = signup["positions"].upper().strip().split(" ")

				signup["scratches"] = signup["scratches"].strip().split(",")

			with open(PARTICIPANTS_FILE, "w") as f:
				json.dump(signups, f, indent=4)

		print("Participants Imported.\n")


class Judge:
	def __init__(self, name, position, scratches):
		self.name = name
		self.position = position
		self.scratches = scratches

	def __str__(self):
		return f"{self.name}"
	
	@staticmethod
	def getJudges():
		with open(PARTICIPANTS_FILE, mode="r") as file:
			participants = json.load(file)

			chairableJudges = []
			panel = []

			for participant in participants:
				if participant["debate/judge"] == "Judge":
					if participant["pro/nov"] == "Pro":
						chairableJudges.append(Judge(participant["name"], position = "Chair", scratches = participant["scratches"]) )
					if participant["pro/nov"] == "Nov":
						panel.append(Judge(participant["name"], position = "Panel", scratches = participant["scratches"]) )

				# Deal with Either later

		print("Judges Made.", "\nChairable Judges:")
		for judge in chairableJudges:
			print(judge)
		print("Panelists:")
		for judge in panel:
			print(judge)
		print("\n")

		return chairableJudges

