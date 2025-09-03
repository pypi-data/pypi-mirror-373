from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup
from ...Internal import Conversions


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RunSelectedCls:
	"""RunSelected commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("runSelected", core, parent)

	def set(self) -> None:
		"""SELFtests:RUNSelected \n
		Snippet: driver.selftests.runSelected.set() \n
		No command help available \n
		"""
		self._core.io.write(f'SELFtests:RUNSelected')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SELFtests:RUNSelected \n
		Snippet: driver.selftests.runSelected.set_and_wait() \n
		No command help available \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SELFtests:RUNSelected', opc_timeout_ms)

	def get(self) -> int:
		"""SELFtests:RUNSelected \n
		Snippet: value: int = driver.selftests.runSelected.get() \n
		No command help available \n
			:return: result: No help available"""
		response = self._core.io.query_str(f'SELFtests:RUNSelected?')
		return Conversions.str_to_int(response)
