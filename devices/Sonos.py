import uuid

from core.commons import constants
from core.device.model.Device import Device
from core.device.model.DeviceAbility import DeviceAbility
from core.webui.model.ClickReactionAction import ClickReactionAction
from core.webui.model.OnClickReaction import OnClickReaction

from ..Sonos import Sonos as sonosSkill

class Sonos(Device):

	@classmethod
	def getDeviceTypeDefinition(cls) -> dict:
		return {
			'deviceTypeName'        : 'Sonos',
			'perLocationLimit'      : 0,
			'totalDeviceLimit'      : 0,
			'allowLocationLinks'    : True,
			'allowHeartbeatOverride': True,
			'heartbeatRate'         : 0,
			'deviceSettings'        : dict(),
			'abilities'             : [DeviceAbility.NONE]
		}


	def onUIClick(self) -> dict:
		if not self.skillInstance:
			return dict()

		skill: sonosSkill = self.skillInstance
		if not self.paired:
			players = skill.sonosPlayers

			reaction = OnClickReaction(
				action=ClickReactionAction.LIST_SELECT.value,
				data={
					'title': skill.randomTalk(text='deviceSelection'),
					'body': skill.randomTalk(text='selectDeviceInList'),
					'list': list(players.keys())
				},
				reply={
					'secret': self.newSecret(),
					'concerns': 'pairing'
				}
			)

			return reaction.toDict()

		return dict()


	def onDeviceUIReply(self, data: dict):
		if not self.checkSecret(secret=data.get('secret', constants.UNKNOWN)):
			return

		if data.get('concerns', '') == 'pairing':
			answer = data.get('answer', '')
			for playername, player in self.skillInstance.sonosPlayers.items():
				if playername == answer:
					self.updateParams('ip', player.ip_address)
					self.pairingDone(uid=str(uuid.uuid4()))
					return
