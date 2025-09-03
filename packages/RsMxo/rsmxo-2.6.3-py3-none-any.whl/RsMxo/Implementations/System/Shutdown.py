from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ShutdownCls:
	"""Shutdown commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("shutdown", core, parent)

	def set(self) -> None:
		"""SYSTem:SHUTdown \n
		Snippet: driver.system.shutdown.set() \n
		Starts the shutdown of the instrument (firmware and operating system) . \n
		"""
		self._core.io.write(f'SYSTem:SHUTdown')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SYSTem:SHUTdown \n
		Snippet: driver.system.shutdown.set_and_wait() \n
		Starts the shutdown of the instrument (firmware and operating system) . \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYSTem:SHUTdown', opc_timeout_ms)
