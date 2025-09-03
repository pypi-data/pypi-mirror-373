from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ColorCls:
	"""Color commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("color", core, parent)

	def set(self, color_signal: enums.ColorSignal, color_value: int) -> None:
		"""DISPlay:COLor:SIGNal:COLor \n
		Snippet: driver.display.color.signal.color.set(color_signal = enums.ColorSignal.C1, color_value = 1) \n
		Sets the color of the selected waveform. \n
			:param color_signal: No help available
			:param color_value: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('color_signal', color_signal, DataType.Enum, enums.ColorSignal), ArgSingle('color_value', color_value, DataType.Integer))
		self._core.io.write(f'DISPlay:COLor:SIGNal:COLor {param}'.rstrip())

	def get(self, color_signal: enums.ColorSignal) -> int:
		"""DISPlay:COLor:SIGNal:COLor \n
		Snippet: value: int = driver.display.color.signal.color.get(color_signal = enums.ColorSignal.C1) \n
		Sets the color of the selected waveform. \n
			:param color_signal: No help available
			:return: color_value: No help available"""
		param = Conversions.enum_scalar_to_str(color_signal, enums.ColorSignal)
		response = self._core.io.query_str(f'DISPlay:COLor:SIGNal:COLor? {param}')
		return Conversions.str_to_int(response)
