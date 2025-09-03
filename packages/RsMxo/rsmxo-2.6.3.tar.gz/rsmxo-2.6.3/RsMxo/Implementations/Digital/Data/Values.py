from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ValuesCls:
	"""Values commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("values", core, parent)

	def get(self, digital=repcap.Digital.Default) -> List[int]:
		"""DIGital<0..15>:DATA[:VALues] \n
		Snippet: value: List[int] = driver.digital.data.values.get(digital = repcap.Digital.Default) \n
		Returns the data of the indicated digital channel for transmission from the instrument to the controlling computer. The
		data can be used in MATLAB, for example. Without parameters, the complete waveform is retrieved. Using the offset and
		length parameters, data can be retrieved in smaller portions, which makes the command faster. If you send only one
		parameter, it is interpreted as offset, and the data is retrieved from offset to the end of the waveform. \n
			:param digital: optional repeated capability selector. Default value: Nr0 (settable in the interface 'Digital')
			:return: digital_data: List of values according to the format and content settings."""
		digital_cmd_val = self._cmd_group.get_repcap_cmd_value(digital, repcap.Digital)
		response = self._core.io.query_bin_or_ascii_int_list(f'FORMAT ASC;DIGital{digital_cmd_val}:DATA:VALues?')
		return response
