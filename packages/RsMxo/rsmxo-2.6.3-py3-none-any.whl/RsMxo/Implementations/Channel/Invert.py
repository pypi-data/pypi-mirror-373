from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class InvertCls:
	"""Invert commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("invert", core, parent)

	def set(self, invert_channel: bool, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:INVert \n
		Snippet: driver.channel.invert.set(invert_channel = False, channel = repcap.Channel.Default) \n
		Turns the inversion of the signal amplitude on or off. To invert means to reflect the voltage values of all signal
		components against the ground level. \n
			:param invert_channel: ON: inverted waveform OFF: normal waveform
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.bool_to_str(invert_channel)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:INVert {param}')

	def get(self, channel=repcap.Channel.Default) -> bool:
		"""CHANnel<*>:INVert \n
		Snippet: value: bool = driver.channel.invert.get(channel = repcap.Channel.Default) \n
		Turns the inversion of the signal amplitude on or off. To invert means to reflect the voltage values of all signal
		components against the ground level. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: invert_channel: ON: inverted waveform OFF: normal waveform"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:INVert?')
		return Conversions.str_to_bool(response)
