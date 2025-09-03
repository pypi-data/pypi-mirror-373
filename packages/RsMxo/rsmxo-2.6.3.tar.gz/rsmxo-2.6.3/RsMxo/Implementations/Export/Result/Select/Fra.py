from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FraCls:
	"""Fra commands group definition. 3 total commands, 0 Subgroups, 3 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fra", core, parent)

	def get_result(self) -> bool:
		"""EXPort:RESult:SELect:FRA:RESult \n
		Snippet: value: bool = driver.export.result.select.fra.get_result() \n
		If enabled, includes the frequency response analysis results, including the frequency, gain, phase and amplitude, in the
		results export file of the FRA. \n
			:return: result: No help available
		"""
		response = self._core.io.query_str('EXPort:RESult:SELect:FRA:RESult?')
		return Conversions.str_to_bool(response)

	def set_result(self, result: bool) -> None:
		"""EXPort:RESult:SELect:FRA:RESult \n
		Snippet: driver.export.result.select.fra.set_result(result = False) \n
		If enabled, includes the frequency response analysis results, including the frequency, gain, phase and amplitude, in the
		results export file of the FRA. \n
			:param result: No help available
		"""
		param = Conversions.bool_to_str(result)
		self._core.io.write(f'EXPort:RESult:SELect:FRA:RESult {param}')

	def get_marker(self) -> bool:
		"""EXPort:RESult:SELect:FRA:MARKer \n
		Snippet: value: bool = driver.export.result.select.fra.get_marker() \n
		If enabled, includes the marker results in the results export file of the FRA. \n
			:return: marker_result: No help available
		"""
		response = self._core.io.query_str('EXPort:RESult:SELect:FRA:MARKer?')
		return Conversions.str_to_bool(response)

	def set_marker(self, marker_result: bool) -> None:
		"""EXPort:RESult:SELect:FRA:MARKer \n
		Snippet: driver.export.result.select.fra.set_marker(marker_result = False) \n
		If enabled, includes the marker results in the results export file of the FRA. \n
			:param marker_result: No help available
		"""
		param = Conversions.bool_to_str(marker_result)
		self._core.io.write(f'EXPort:RESult:SELect:FRA:MARKer {param}')

	def get_margin(self) -> bool:
		"""EXPort:RESult:SELect:FRA:MARGin \n
		Snippet: value: bool = driver.export.result.select.fra.get_margin() \n
		If enabled, includes the margin results in the results export file of the FRA. \n
			:return: margin_result: No help available
		"""
		response = self._core.io.query_str('EXPort:RESult:SELect:FRA:MARGin?')
		return Conversions.str_to_bool(response)

	def set_margin(self, margin_result: bool) -> None:
		"""EXPort:RESult:SELect:FRA:MARGin \n
		Snippet: driver.export.result.select.fra.set_margin(margin_result = False) \n
		If enabled, includes the margin results in the results export file of the FRA. \n
			:param margin_result: No help available
		"""
		param = Conversions.bool_to_str(margin_result)
		self._core.io.write(f'EXPort:RESult:SELect:FRA:MARGin {param}')
