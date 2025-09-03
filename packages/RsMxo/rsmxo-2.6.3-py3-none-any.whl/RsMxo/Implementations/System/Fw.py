from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions
from ...Internal.Utilities import trim_str_response


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class FwCls:
	"""Fw commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("fw", core, parent)

	def get_file_path(self) -> str:
		"""SYSTem:FW:FILepath \n
		Snippet: value: str = driver.system.fw.get_file_path() \n
		Sets the path and the filename of the firmware installation file. \n
			:return: file_path: String with path and filename
		"""
		response = self._core.io.query_str('SYSTem:FW:FILepath?')
		return trim_str_response(response)

	def set_file_path(self, file_path: str) -> None:
		"""SYSTem:FW:FILepath \n
		Snippet: driver.system.fw.set_file_path(file_path = 'abc') \n
		Sets the path and the filename of the firmware installation file. \n
			:param file_path: String with path and filename
		"""
		param = Conversions.value_to_quoted_str(file_path)
		self._core.io.write(f'SYSTem:FW:FILepath {param}')

	def start(self) -> None:
		"""SYSTem:FW:STARt \n
		Snippet: driver.system.fw.start() \n
		Starts the firmware update. Before starting, make sure that the correct path is set with method RsMxo.System.Fw.filePath. \n
		"""
		self._core.io.write(f'SYSTem:FW:STARt')

	def start_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SYSTem:FW:STARt \n
		Snippet: driver.system.fw.start_and_wait() \n
		Starts the firmware update. Before starting, make sure that the correct path is set with method RsMxo.System.Fw.filePath. \n
		Same as start, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYSTem:FW:STARt', opc_timeout_ms)
