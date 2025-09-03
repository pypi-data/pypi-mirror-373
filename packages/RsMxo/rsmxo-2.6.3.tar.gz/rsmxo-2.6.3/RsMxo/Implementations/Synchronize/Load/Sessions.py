from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class SessionsCls:
	"""Sessions commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("sessions", core, parent)

	def set(self) -> None:
		"""SYNChronize:LOAD:SESSion \n
		Snippet: driver.synchronize.load.sessions.set() \n
		No command help available \n
		"""
		self._core.io.write(f'SYNChronize:LOAD:SESSion')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SYNChronize:LOAD:SESSion \n
		Snippet: driver.synchronize.load.sessions.set_and_wait() \n
		No command help available \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYNChronize:LOAD:SESSion', opc_timeout_ms)
