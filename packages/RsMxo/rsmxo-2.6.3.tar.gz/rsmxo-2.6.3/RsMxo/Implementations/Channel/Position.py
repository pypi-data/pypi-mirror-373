from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PositionCls:
	"""Position commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("position", core, parent)

	def set(self, position: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:POSition \n
		Snippet: driver.channel.position.set(position = 1.0, channel = repcap.Channel.Default) \n
		Moves the selected signal up or down in the diagram. While the offset sets a voltage, position is a graphical setting
		given in divisions. The visual effect is the same as for offset. \n
			:param position: Positive values move up the waveform, negative values move it down.
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(position)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:POSition {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:POSition \n
		Snippet: value: float = driver.channel.position.get(channel = repcap.Channel.Default) \n
		Moves the selected signal up or down in the diagram. While the offset sets a voltage, position is a graphical setting
		given in divisions. The visual effect is the same as for offset. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: position: Positive values move up the waveform, negative values move it down."""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:POSition?')
		return Conversions.str_to_float(response)
