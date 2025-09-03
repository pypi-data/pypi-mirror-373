from ..Internal.Core import Core
from ..Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class AutoScaleCls:
	"""AutoScale commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("autoScale", core, parent)

	def set(self) -> None:
		"""AUToscale \n
		Snippet: driver.autoScale.set() \n
		Performs an autoset process: analyzes the enabled channel signals, and obtains appropriate horizontal, vertical, and
		trigger settings to display stable waveforms. Rohde & Schwarz does not recommend using the autoset in remote control. To
		adjust the oscilloscope remotely, especially for automated testing applications, use the remote commands that adjust the
		horizontal, vertical and trigger settings. \n
		"""
		self._core.io.write(f'AUToscale')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""AUToscale \n
		Snippet: driver.autoScale.set_and_wait() \n
		Performs an autoset process: analyzes the enabled channel signals, and obtains appropriate horizontal, vertical, and
		trigger settings to display stable waveforms. Rohde & Schwarz does not recommend using the autoset in remote control. To
		adjust the oscilloscope remotely, especially for automated testing applications, use the remote commands that adjust the
		horizontal, vertical and trigger settings. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'AUToscale', opc_timeout_ms)
