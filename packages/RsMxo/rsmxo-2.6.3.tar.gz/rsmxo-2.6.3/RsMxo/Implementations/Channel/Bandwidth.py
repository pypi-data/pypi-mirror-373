from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BandwidthCls:
	"""Bandwidth commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("bandwidth", core, parent)

	def set(self, bandwidth_limit: float, channel=repcap.Channel.Default) -> None:
		"""CHANnel<*>:BANDwidth \n
		Snippet: driver.channel.bandwidth.set(bandwidth_limit = 1.0, channel = repcap.Channel.Default) \n
		Sets the bandwidth limit. The specified bandwidth indicates the range of frequencies that the instrument can acquire and
		display accurately with less than 3 dB attenuation. Frequencies above the limit are removed from the signal, and noise is
		reduced. \n
			:param bandwidth_limit:
				- FULL: Sets the bandwidth to the maximum bandwidth of the instrument. Bandwidth extension options are considered.
				- B700 | B500 | B350 | B200 | B100 | B50 | B20: Sets a bandwidth limit lower than the maximum. The number indicates the bandwidth limit in MHz.
				- B1G5 | B1G: Sets the bandwidth limit to 1500 MHz or 1000 MHz if these values are lower than the maximum.
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')"""
		param = Conversions.decimal_value_to_str(bandwidth_limit)
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		self._core.io.write(f'CHANnel{channel_cmd_val}:BANDwidth {param}')

	def get(self, channel=repcap.Channel.Default) -> float:
		"""CHANnel<*>:BANDwidth \n
		Snippet: value: float = driver.channel.bandwidth.get(channel = repcap.Channel.Default) \n
		Sets the bandwidth limit. The specified bandwidth indicates the range of frequencies that the instrument can acquire and
		display accurately with less than 3 dB attenuation. Frequencies above the limit are removed from the signal, and noise is
		reduced. \n
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: result: Possible results, availability depends on the maximum bandwidth of the instrument and bandwidth extension options."""
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_str(f'CHANnel{channel_cmd_val}:BANDwidth?')
		return Conversions.str_to_float(response)
