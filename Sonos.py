from typing import Dict, List, Optional

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
		if 'Action' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', skill='system')
			)
			return

		action = session.slotValue('Action') if 'Action' in session.slots else 'play'
		players = self.filterPlayers(session)

		if not players:
			return

		for player in players:
			self.action(player, action)

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='ok')
		)


	@IntentHandler('ChangeTrack')
	def changeTrack(self, session: DialogSession, **_kwargs):
		if 'Direction' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', skill='system')
			)
			return

		players = self.filterPlayers(session)
		if not players:
			return

		for player in players:
			self.action(player, session.slotValue('Direction'))

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='ok')
		)


	@IntentHandler('SetSonosVolume')
	def changeVolume(self, session: DialogSession, **_kwargs):
		if 'VolumeDirection' not in session.slots and 'ExactVolume' not in session.slots:
			self.continueDialog(
				sessionId=session.sessionId,
				text=self.TalkManager.randomTalk('notUnderstood', skill='system')
			)
			return

		players = self.filterPlayers(session)
		if not players:
			return

		for player in players:
			volume = player.volume

			if 'ExactVolume' in session.slots:
				volume = self.Commons.clamp(float(session.slotValue('ExactVolume')), 0, 100)
			else:
				if session.slotValue('VolumeDirection') == 'louder':
					volume = self.Commons.clamp(volume + 10, 0, 100)
				else:
					volume = self.Commons.clamp(volume - 10, 0, 100)

			player.ramp_to_volume(int(volume))

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='ok')
		)


	def filterPlayers(self, session: DialogSession) -> Optional[List[SoCo]]:
		room = session.slots['Room'].lower() if 'Room' in session.slots else session.siteId

		if room == constants.EVERYWHERE:
			return [player for player in self._sonosPlayers.values()]

		if room not in self._sonosPlayers:
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='noPlayerInRoom', replace=[room])
			)
			return None

		return [self._sonosPlayers[room]]


	@staticmethod
	def action(player: SoCo, action: str):
		if action == 'play':
			player.play()
		elif action == 'stop':
			player.stop()
		elif action == 'pause':
			player.pause()
		elif action == 'next':
			player.next()
		elif action == 'previous':
			player.previous()
