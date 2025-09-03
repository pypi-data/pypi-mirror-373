from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RangeCls:
	"""Range commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("range", core, parent)

	def set(self, range_py: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:RANGe \n
		Snippet: driver.channel.range.set(range_py = 1.0, channel = repcap.Channel.Default) \n
		Sets the voltage range across the 10 vertical divisions of the diagram. The command is an alternative to method RsMxo.
		Channel.Scale.set. \n
			:param range_py: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(range_py)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:RANGe {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:RANGe \n
		Snippet: value: float = driver.channel.range.get(channel = repcap.Channel.Default) \n
		Sets the voltage range across the 10 vertical divisions of the diagram. The command is an alternative to method RsMxo.
		Channel.Scale.set. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: range_py: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:RANGe?')
		return Conversions.str_to_float(response)
