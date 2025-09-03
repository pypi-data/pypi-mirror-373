from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DlcValueCls:
	"""DlcValue commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("dlcValue", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default) -> int:
		"""SBUS<*>:CAN:FRAMe<*>:DLCValue \n
		Snippet: value: int = driver.sbus.can.frame.dlcValue.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default) \n
		Returns the data length code of the selected frame - the number of data bytes in the frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:return: frame_dlc_value: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:DLCValue?')
		return Conversions.str_to_int(response)
