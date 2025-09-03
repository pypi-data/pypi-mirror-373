from typing import List

from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class Fd2ValueCls:
	"""Fd2Value commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fd2Value", core, parent)

	def set(self, field_2_value: List[int], measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:PROTocol:FD2Value \n
		Snippet: driver.measurement.protocol.fd2Value.set(field_2_value = [1, 2, 3], measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param field_2_value: List of comma separated values
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.list_to_csv_str(field_2_value)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:PROTocol:FD2Value {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> List[int]:
		"""MEASurement<*>:PROTocol:FD2Value \n
		Snippet: value: List[int] = driver.measurement.protocol.fd2Value.get(measIndex = repcap.MeasIndex.Default) \n
		Sets or queries the one or more values of the field, at which the oscilloscope ends the measurement in a From - To
		condition. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: field_2_value: List of comma separated values"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_bin_or_ascii_int_list(f'MEASurement{measIndex_cmd_val}:PROTocol:FD2Value?')
		return response
