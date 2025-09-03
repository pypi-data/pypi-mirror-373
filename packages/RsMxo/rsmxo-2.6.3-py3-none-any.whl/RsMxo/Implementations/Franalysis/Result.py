from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	def get_state(self) -> bool:
		"""FRANalysis:RESult:STATe \n
		Snippet: value: bool = driver.franalysis.result.get_state() \n
		Enables the display of the result table for the FRA. \n
			:return: table: No help available
		"""
		response = self._core.io.query_str('FRANalysis:RESult:STATe?')
		return Conversions.str_to_bool(response)

	def set_state(self, table: bool) -> None:
		"""FRANalysis:RESult:STATe \n
		Snippet: driver.franalysis.result.set_state(table = False) \n
		Enables the display of the result table for the FRA. \n
			:param table: No help available
		"""
		param = Conversions.bool_to_str(table)
		self._core.io.write(f'FRANalysis:RESult:STATe {param}')
