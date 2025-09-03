from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from ..... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SamplePointCls:
	"""SamplePoint commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("samplePoint", core, parent)

	def set(self, xl_sample_point: float, serialBus=repcap.SerialBus.Default) -> None:
		"""SBUS<*>:CAN:XDATa:SAMPlepoint \n
		Snippet: driver.sbus.can.xdata.samplePoint.set(xl_sample_point = 1.0, serialBus = repcap.SerialBus.Default) \n
		Sets the position of the sample point within the bit in percent of the nominal bit time for the CAN XL frame. \n
			:param xl_sample_point: No help available
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
		"""
		param = Conversions.decimal_value_to_str(xl_sample_point)
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		self._core.io.write(f'SBUS{serialBus_cmd_val}:CAN:XDATa:SAMPlepoint {param}')

	def get(self, serialBus=repcap.SerialBus.Default) -> float:
		"""SBUS<*>:CAN:XDATa:SAMPlepoint \n
		Snippet: value: float = driver.sbus.can.xdata.samplePoint.get(serialBus = repcap.SerialBus.Default) \n
		Sets the position of the sample point within the bit in percent of the nominal bit time for the CAN XL frame. \n
			:param serialBus: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Sbus')
			:return: xl_sample_point: No help available"""
		serialBus_cmd_val = self._cmd_group.get_repcap_cmd_value(serialBus, repcap.SerialBus)
		response = self._core.io.query_str(f'SBUS{serialBus_cmd_val}:CAN:XDATa:SAMPlepoint?')
		return Conversions.str_to_float(response)
