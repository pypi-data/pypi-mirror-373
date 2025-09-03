from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SwtTimeCls:
	"""SwtTime commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("swtTime", core, parent)

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:QSPI:SWTTime \n
		Snippet: value: float = driver.sbus.qspi.swtTime.get(serialBus = repcap.SerialBus.Default) \n
		Queries the software trigger time in seconds. If no software trigger event has occured, the command returns Invalid. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: time: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:QSPI:SWTTime?')
		return Conversions.str_to_float(response)
