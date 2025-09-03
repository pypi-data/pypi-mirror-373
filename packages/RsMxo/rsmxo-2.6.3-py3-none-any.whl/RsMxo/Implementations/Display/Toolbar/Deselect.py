from ....Internal.Core import Core
from ....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class DeselectCls:
	"""Deselect commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("deselect", core, parent)

	def set(self) -> None:
		"""DISPlay:TOOLbar:DESelect \n
		Snippet: driver.display.toolbar.deselect.set() \n
		Removes all tools from the toolbar. \n
		"""
		self._core.io.write(f'DISPlay:TOOLbar:DESelect')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""DISPlay:TOOLbar:DESelect \n
		Snippet: driver.display.toolbar.deselect.set_and_wait() \n
		Removes all tools from the toolbar. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'DISPlay:TOOLbar:DESelect', opc_timeout_ms)
