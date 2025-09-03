from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ResPathCls:
	"""ResPath commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("resPath", core, parent)

	def set(self) -> None:
		"""MMEMory:AUTonaming:RESPath \n
		Snippet: driver.massMemory.autoNaming.resPath.set() \n
		Resets the path for file operations to the factory default path. \n
		"""
		self._core.io.write(f'MMEMory:AUTonaming:RESPath')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""MMEMory:AUTonaming:RESPath \n
		Snippet: driver.massMemory.autoNaming.resPath.set_and_wait() \n
		Resets the path for file operations to the factory default path. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'MMEMory:AUTonaming:RESPath', opc_timeout_ms)
