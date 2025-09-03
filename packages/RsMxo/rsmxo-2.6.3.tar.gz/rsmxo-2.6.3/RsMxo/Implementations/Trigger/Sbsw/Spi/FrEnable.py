from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FrEnableCls:
	"""FrEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("frEnable", core, parent)

	def set(self, frame: str, enabler: bool) -> None:
		"""TRIGger:SBSW:SPI:FRENable \n
		Snippet: driver.trigger.sbsw.spi.frEnable.set(frame = 'abc', enabler = False) \n
		Enables or disables the checking condition for the selected frame for the software trigger. \n
			:param frame: No help available
			:param enabler: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('frame', frame, DataType.String), ArgSingle('enabler', enabler, DataType.Boolean))
		self._core.io.write(f'TRIGger:SBSW:SPI:FRENable {param}'.rstrip())

	def get(self) -> bool:
		"""TRIGger:SBSW:SPI:FRENable \n
		Snippet: value: bool = driver.trigger.sbsw.spi.frEnable.get() \n
		Enables or disables the checking condition for the selected frame for the software trigger. \n
			:return: enabler: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:SPI:FRENable?')
		return Conversions.str_to_bool(response)
