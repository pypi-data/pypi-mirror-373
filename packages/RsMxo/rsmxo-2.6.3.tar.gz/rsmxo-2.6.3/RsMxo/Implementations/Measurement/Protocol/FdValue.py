from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FdValueCls:
	"""FdValue commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fdValue", core, parent)

	def set(self, field_value: List[int], measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:PROTocol:FDValue \n
		Snippet: driver.measurement.protocol.fdValue.set(field_value = [1, 2, 3], measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope executes or starts the measurement. \n
			:param field_value: List of comma separated values
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.list_to_csv_str(field_value)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:PROTocol:FDValue {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> List[int]:
		"""MEASurement<*>:PROTocol:FDValue \n
		Snippet: value: List[int] = driver.measurement.protocol.fdValue.get(measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope executes or starts the measurement. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: field_value: List of comma separated values"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_bin_or_ascii_int_list(f'MEASurement{measIndex_cmd_val}:PROTocol:FDValue?')
		return response
