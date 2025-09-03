from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Types import DataType
from ....Internal.ArgSingleList import ArgSingleList
from ....Internal.ArgSingle import ArgSingle
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesPartialCls:
	"""ValuesPartial commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("valuesPartial", core, parent)

	def get(self, offset: int, length: int, channel=repcap.Channel.Default) -> List[float]:
		"""CHANnel<1..8>:DATA[:VALues] \n
		Snippet: value: List[float] = driver.channel.data.valuesPartial.get(offset = 1, length = 1, channel = repcap.Channel.Default) \n
		Returns the data of the channel waveform points for transmission from the instrument to the controlling computer.
		The data can be used in MATLAB, for example. Without parameters, the complete waveform is retrieved. Using the offset and
		length parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one
		parameter, it is interpreted as offset, and the data is retrieved from offset to the end of the waveform. To set the
		export format, use method RsMxo.FormatPy.Data.set. \n
			:param offset: Number of offset waveform samples to be skipped. Range: 0 to m. Limit: n + m = record length
			:param length: Number of waveform points to be retrieved.
			:param channel: optional repeated capability selector. Default value: Ch1 (settable in the interface 'Channel')
			:return: waveform_data: List of values according to the format and content settings."""
		param = ArgSingleList().compose_cmd_string(ArgSingle('offset', offset, DataType.Integer), ArgSingle('length', length, DataType.Integer))
		channel_cmd_val = self._cmd_group.get_repcap_cmd_value(channel, repcap.Channel)
		response = self._core.io.query_bin_or_ascii_float_list(f'FORMAT REAL,32;CHANnel{channel_cmd_val}:DATA:VALues? {param}'.rstrip())
		return response
