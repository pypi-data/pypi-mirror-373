from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class PtCountCls:
	"""PtCount commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("ptCount", core, parent)

	def set(self, pulse_count: int, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:AMPTime:PTCount \n
		Snippet: driver.measurement.ampTime.ptCount.set(pulse_count = 1, measIndex = repcap.MeasIndex.Default) \n
		Sets the number of positive pulses for the pulse train measurement. It measures the duration of N positive pulses from
		the rising edge of the first pulse to the falling edge of the N-th pulse. \n
			:param pulse_count: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.decimal_value_to_str(pulse_count)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:AMPTime:PTCount {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> int:
		"""MEASurement<*>:AMPTime:PTCount \n
		Snippet: value: int = driver.measurement.ampTime.ptCount.get(measIndex = repcap.MeasIndex.Default) \n
		Sets the number of positive pulses for the pulse train measurement. It measures the duration of N positive pulses from
		the rising edge of the first pulse to the falling edge of the N-th pulse. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: pulse_count: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:AMPTime:PTCount?')
		return Conversions.str_to_int(response)
