from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ExitCls:
	"""Exit commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("exit", core, parent)

	def set(self) -> None:
		"""SYSTem:EXIT \n
		Snippet: driver.system.exit.set() \n
		Starts the shutdown of the firmware. \n
		"""
		self._core.io.write(f'SYSTem:EXIT')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""SYSTem:EXIT \n
		Snippet: driver.system.exit.set_and_wait() \n
		Starts the shutdown of the firmware. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'SYSTem:EXIT', opc_timeout_ms)
