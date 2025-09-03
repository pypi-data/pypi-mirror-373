from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResAllCls:
	"""ResAll commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("resAll", core, parent)

	def set(self) -> None:
		"""MMEMory:AUTonaming:RESall \n
		Snippet: driver.massMemory.autoNaming.resAll.set() \n
		Resets all autonaming settings to the default value, including the path. \n
		"""
		self._core.io.write(f'MMEMory:AUTonaming:RESall')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""MMEMory:AUTonaming:RESall \n
		Snippet: driver.massMemory.autoNaming.resAll.set_and_wait() \n
		Resets all autonaming settings to the default value, including the path. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MMEMory:AUTonaming:RESall', opc_timeout_ms)
