from typing import Dict

import soco
from soco import SoCo

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.commons import constants
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class Sonos(AliceSkill):
	"""
	Author: Psychokiller1888
	Description: Let alice control your sonos hardware
	"""

	def __init__(self):
		super().__init__()
		self._sonosPlayers: Dict[str, SoCo] = dict()


	def onStart(self):
		super().onStart()

		self._sonosPlayers = {device.player_name.lower(): device for device in soco.discover()}

		if not self._sonosPlayers:
			self.logWarning('No Sonos device found')
			raise SkillStartingFailed


	@IntentHandler('PlayStopPauseSonos')
	def playStopPause(self, session: DialogSession, **_kwargs):
		action = session.slots['Action'] if 'Action' in session.slots else 'play'
		room = session.slots['Room'].lower() if 'Room' in session.slots else session.siteId

		if room not in self._sonosPlayers and room != constants.EVERYWHERE:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='noPlayerInRoom', replace=[room])
			)
			return

		if room == constants.EVERYWHERE:
			for room in self._sonosPlayers:
				self.action(room, action)
		else:
			self.action(room, action)

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='ok')
		)


	def action(self, room: str, action: str):
		if action == 'play':
			self._sonosPlayers[room].play()
		elif action == 'stop':
			self._sonosPlayers[room].stop()
		else:
			self._sonosPlayers[room].pause()
