from typing import List

from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DataCls:
	"""Data commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("data", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> List[int]:
		"""SBUS<*>:SPI:FRAMe<*>:DATA \n
		Snippet: value: List[int] = driver.sbus.spi.frame.data.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the data words of the specified frame in comma-separated values. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_data: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_bin_or_ascii_int_list(f'SBUS{serialBus_cmd_val}:SPI:FRAMe{frame_cmd_val}:DATA?')
		return response
