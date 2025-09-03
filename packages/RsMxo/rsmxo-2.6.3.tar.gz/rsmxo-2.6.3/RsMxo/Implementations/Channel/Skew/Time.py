from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class TimeCls:
	"""Time commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("time", core, parent)

	def set(self, offset: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:SKEW:TIME \n
		Snippet: driver.channel.skew.time.set(offset = 1.0, channel = repcap.Channel.Default) \n
		Sets a skew value to compensate for the delay of the measurement setup or from the circuit specifics that the instrument
		cannot compensate automatically. It affects only the selected input channel. \n
			:param offset: No help available
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
		"""
		param = Conversions.decimal_value_to_str(offset)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:SKEW:TIME {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:SKEW:TIME \n
		Snippet: value: float = driver.channel.skew.time.get(channel = repcap.Channel.Default) \n
		Sets a skew value to compensate for the delay of the measurement setup or from the circuit specifics that the instrument
		cannot compensate automatically. It affects only the selected input channel. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: offset: No help available"""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:SKEW:TIME?')
		return Conversions.str_to_float(response)
