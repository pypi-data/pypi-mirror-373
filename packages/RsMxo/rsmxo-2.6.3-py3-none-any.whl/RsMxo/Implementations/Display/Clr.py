from ...Internal.Core import Core
from ...Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class ClrCls:
	"""Clr commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("clr", core, parent)

	def set(self) -> None:
		"""DISPlay:CLR \n
		Snippet: driver.display.clr.set() \n
		Deletes all measurement results including all waveforms and statistics. \n
		"""
		self._core.io.write(f'DISPlay:CLR')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""DISPlay:CLR \n
		Snippet: driver.display.clr.set_and_wait() \n
		Deletes all measurement results including all waveforms and statistics. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:CLR', opc_timeout_ms)
