from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AllCls:
	"""All commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("all", core, parent)

	def set(self) -> None:
		"""CALibration[:ALL] \n
		Snippet: driver.calibration.all.set() \n
		Calibration:ALL starts the self-alignment process without returning status information. To get the status, use the
		commands of the operation status register. Calibration:ALL? starts the self-alignment process and returns information on
		the state of the self-alignment. (Same as *CAL?) . The process can take several minutes. Consider your timeout settings. \n
		"""
		self._core.io.write(f'CALibration:ALL')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""CALibration[:ALL] \n
		Snippet: driver.calibration.all.set_and_wait() \n
		Calibration:ALL starts the self-alignment process without returning status information. To get the status, use the
		commands of the operation status register. Calibration:ALL? starts the self-alignment process and returns information on
		the state of the self-alignment. (Same as *CAL?) . The process can take several minutes. Consider your timeout settings. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'CALibration:ALL', opc_timeout_ms)
