from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ScaleCls:
	"""Scale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("scale", core, parent)

	def set(self, scale: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:SCALe \n
		Snippet: driver.channel.scale.set(scale = 1.0, channel = repcap.Channel.Default) \n
		Sets the vertical scale, which defines the displayed amplitude of the selected waveform. \n
			:param scale: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(scale)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:SCALe {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:SCALe \n
		Snippet: value: float = driver.channel.scale.get(channel = repcap.Channel.Default) \n
		Sets the vertical scale, which defines the displayed amplitude of the selected waveform. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: scale: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:SCALe?')
		return Conversions.str_to_float(response)
