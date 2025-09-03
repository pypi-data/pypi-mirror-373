from ......Internal.Core import Core
from ......Internal.CommandsGroup import CommandsGroup
from ......Internal import Conversions
from ...... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class BrsCls:
	"""Brs commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("brs", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default, frame=repcap.Frame.Default, fieldData=repcap.FieldData.Default) -> int:
		"""SBUS<*>:CAN:FRAMe<*>:FDATa<*>:BRS \n
		Snippet: value: int = driver.sbus.can.frame.fdata.brs.get(serialBus = repcap.SerialBus.Default, frame = repcap.Frame.Default, fieldData = repcap.FieldData.Default) \n
		Returns the value of the bit rate switch (BRS) field for the selected frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:param frame: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Frame')
			:param fieldData: optional repeated capability selector. Default value: Ix1 (settable in the interface 'Fdata')
			:return: brs: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		frame_cmd_val = self._cmd_group.get_repcap_cmd_value(frame, repcap.Frame)
		fieldData_cmd_val = self._cmd_group.get_repcap_cmd_value(fieldData, repcap.FieldData)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:FRAMe{frame_cmd_val}:FDATa{fieldData_cmd_val}:BRS?')
		return Conversions.str_to_int(response)
