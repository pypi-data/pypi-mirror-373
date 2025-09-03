from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ForceCls:
	"""Force commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("force", core, parent)

	def set(self) -> None:
		"""TRIGger:FORCe \n
		Snippet: driver.trigger.force.set() \n
		Provokes an immediate single acquisition. Force the trigger if the acquisition is running in normal mode and no valid
		trigger occurs. Thus, you can confirm that a signal is available and use the waveform display to determine how to trigger
		on it. \n
		"""
		self._core.io.write(f'TRIGger:FORCe')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""TRIGger:FORCe \n
		Snippet: driver.trigger.force.set_and_wait() \n
		Provokes an immediate single acquisition. Force the trigger if the acquisition is running in normal mode and no valid
		trigger occurs. Thus, you can confirm that a signal is available and use the waveform display to determine how to trigger
		on it. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'TRIGger:FORCe', opc_timeout_ms)
