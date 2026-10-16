from participants import Participants, Team, Judge
from draws.slotting import Room


Participants.importParticipants()

draw = Room.makeRooms()
for room in draw:
	print(room)

