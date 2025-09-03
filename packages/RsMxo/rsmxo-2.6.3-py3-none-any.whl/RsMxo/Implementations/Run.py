from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RunCls:
	"""Run commands group definition. 2 total commands, 0 Subgroups, 2 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("run", core, parent)

	def continuous(self) -> None:
		"""RUNCont \n
		Snippet: driver.run.continuous() \n
		Starts the continuous acquisition. \n
		"""
		self._core.io.write(f'RUNCont')
		# OpcSyncAllowed = false

	def single(self) -> None:
		"""RUNSingle \n
		Snippet: driver.run.single() \n
		Starts a defined number of acquisition cycles. The number of cycles is set with method RsMxo.Acquire.count. \n
		"""
		self._core.io.write(f'RUNSingle')

	def single_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""RUNSingle \n
		Snippet: driver.run.single_and_wait() \n
		Starts a defined number of acquisition cycles. The number of cycles is set with method RsMxo.Acquire.count. \n
		Same as single, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'RUNSingle', opc_timeout_ms)
