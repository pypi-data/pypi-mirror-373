from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResultCls:
	"""Result commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("result", core, parent)

	def get_fontsize(self) -> int:
		"""DISPlay:RESult:FONTsize \n
		Snippet: value: int = driver.display.result.get_fontsize() \n
		Sets the font size of the text in result tables. \n
			:return: result_font_size: No help available
		"""
		response = self._core.io.query_str('DISPlay:RESult:FONTsize?')
		return Conversions.str_to_int(response)

	def set_fontsize(self, result_font_size: int) -> None:
		"""DISPlay:RESult:FONTsize \n
		Snippet: driver.display.result.set_fontsize(result_font_size = 1) \n
		Sets the font size of the text in result tables. \n
			:param result_font_size: No help available
		"""
		param = Conversions.decimal_value_to_str(result_font_size)
		self._core.io.write(f'DISPlay:RESult:FONTsize {param}')
