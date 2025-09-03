from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle
from ..... import enums


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class UseCls:
	"""Use commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("use", core, parent)

	def set(self, color_signal: enums.ColorSignal, state: bool) -> None:
		"""DISPlay:COLor:SIGNal:USE \n
		Snippet: driver.display.color.signal.use.set(color_signal = enums.ColorSignal.C1, state = False) \n
		If enabled, the selected waveform is displayed according to its assigned color table. If disabled, the selected color is
		displayed, and the intensity of the signal color varies according to the cumulative occurrence of the values. The setting
		is not available for digital channels and parallel buses. \n
			:param color_signal: No help available
			:param state: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('color_signal', color_signal, DataType.Enum, enums.ColorSignal), ArgSingle('state', state, DataType.Boolean))
		self._core.io.write(f'DISPlay:COLor:SIGNal:USE {param}'.rstrip())

	def get(self, color_signal: enums.ColorSignal) -> bool:
		"""DISPlay:COLor:SIGNal:USE \n
		Snippet: value: bool = driver.display.color.signal.use.get(color_signal = enums.ColorSignal.C1) \n
		If enabled, the selected waveform is displayed according to its assigned color table. If disabled, the selected color is
		displayed, and the intensity of the signal color varies according to the cumulative occurrence of the values. The setting
		is not available for digital channels and parallel buses. \n
			:param color_signal: Signal name as returned by method RsMxo.Display.Color.Signal.catalog.
			:return: state: No help available"""
		param = Conversions.enum_scalar_to_str(color_signal, enums.ColorSignal)
		response = self._core.io.query_str(f'DISPlay:COLor:SIGNal:USE? {param}')
		return Conversions.str_to_bool(response)
