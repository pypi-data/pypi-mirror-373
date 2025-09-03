from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup
from ....Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColorCls:
	"""Color commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("color", core, parent)

	def get_catalog(self) -> str:
		"""DISPlay:ANNotation:COLor:CATalog \n
		Snippet: value: str = driver.display.annotation.color.get_catalog() \n
		Returns the list of possible colors, see Table 'Color catalog for annotations'. \n
			:return: color_catalog: String parameter, comma-separated values
		"""
		response = self._core.io.query_str('DISPlay:ANNotation:COLor:CATalog?')
		return trim_str_response(response)
