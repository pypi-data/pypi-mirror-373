from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PcRcCls:
	"""PcRc commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("pcRc", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, xdata=repcap.Xdata.Default) -> int:
		"""SBUS<*>:CAN:FRAMe<*>:XDATa<*>:PCRC \n
		Snippet: value: int = driver.sbus.can.frame.xdata.pcRc.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, xdata = repcap.Xdata.Default) \n
		Returns the value of the preamble cyclic redundant check (PCRC) for the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param xdata: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Xdata')
			:return: pc_rc: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		xdata_cmd_val = self._cmd_group.get_repcap_cmd_value(xdata, repcap.Xdata)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:XDATa{xdata_cmd_val}:PCRC?')
		return Conversions.str_to_int(response)
