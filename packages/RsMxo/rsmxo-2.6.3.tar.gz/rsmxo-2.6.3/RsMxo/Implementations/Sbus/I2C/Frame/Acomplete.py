from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AcompleteCls:
	"""Acomplete commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("acomplete", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> bool:
		"""SBUS<*>:I2C:FRAMe<*>:ACOMplete \n
		Snippet: value: bool = driver.sbus.i2C.frame.acomplete.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns if the address is completely contained in the acquisition. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: addr_complete: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:I2C:FRAMe{frame_cmd_val}:ACOMplete?')
		return Conversions.str_to_bool(response)
