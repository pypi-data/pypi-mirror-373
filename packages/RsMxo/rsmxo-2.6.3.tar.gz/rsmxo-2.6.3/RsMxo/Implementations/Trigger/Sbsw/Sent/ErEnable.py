from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup
from .....Internal import Conversions
from .....Internal.Types import DataType
from .....Internal.ArgSingleList import ArgSingleList
from .....Internal.ArgSingle import ArgSingle


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ErEnableCls:
	"""ErEnable commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("erEnable", core, parent)

	def set(self, error_name: str, enabler: bool) -> None:
		"""TRIGger:SBSW:SENT:ERENable \n
		Snippet: driver.trigger.sbsw.sent.erEnable.set(error_name = 'abc', enabler = False) \n
		Defines the error type for the software trigger. \n
			:param error_name: No help available
			:param enabler: No help available
		"""
		param = ArgSingleList().compose_cmd_string(ArgSingle('error_name', error_name, DataType.String), ArgSingle('enabler', enabler, DataType.Boolean))
		self._core.io.write(f'TRIGger:SBSW:SENT:ERENable {param}'.rstrip())

	def get(self) -> bool:
		"""TRIGger:SBSW:SENT:ERENable \n
		Snippet: value: bool = driver.trigger.sbsw.sent.erEnable.get() \n
		Defines the error type for the software trigger. \n
			:return: enabler: No help available"""
		response = self._core.io.query_str(f'TRIGger:SBSW:SENT:ERENable?')
		return Conversions.str_to_bool(response)
