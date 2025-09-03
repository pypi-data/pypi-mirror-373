from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal import Conversions
from .... import repcap


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultsCls:
	"""Results commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("results", core, parent)

	def set(self, disp_res_lines: bool, measIndex=repcap.MeasIndex.Default) -> None:
		"""MEASurement<*>:DISPlay:RESults \n
		Snippet: driver.measurement.display.results.set(disp_res_lines = False, measIndex = repcap.MeasIndex.Default) \n
		Enables the measurement annotations for the selected measurement. These annotations are, for example, periods, maximum
		and minimum values, relevant reference levels, and more. \n
			:param disp_res_lines: No help available
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
		"""
		param = Conversions.bool_to_str(disp_res_lines)
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		self._core.io.write(f'MEASurement{measIndex_cmd_val}:DISPlay:RESults {param}')

	def get(self, measIndex=repcap.MeasIndex.Default) -> bool:
		"""MEASurement<*>:DISPlay:RESults \n
		Snippet: value: bool = driver.measurement.display.results.get(measIndex = repcap.MeasIndex.Default) \n
		Enables the measurement annotations for the selected measurement. These annotations are, for example, periods, maximum
		and minimum values, relevant reference levels, and more. \n
			:param measIndex: optional repeated capability selector. Default value: Nr1 (settable in the interface 'Measurement')
			:return: disp_res_lines: No help available"""
		measIndex_cmd_val = self._cmd_group.get_repcap_cmd_value(measIndex, repcap.MeasIndex)
		response = self._core.io.query_str(f'MEASurement{measIndex_cmd_val}:DISPlay:RESults?')
		return Conversions.str_to_bool(response)
