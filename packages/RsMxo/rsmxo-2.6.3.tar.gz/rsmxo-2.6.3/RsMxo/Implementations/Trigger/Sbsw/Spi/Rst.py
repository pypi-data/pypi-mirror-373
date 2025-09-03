from .....Internal.Core import Core
from .....Internal.CommandsGroup import CommandsGroup


# noinspection PyPep8Naming,PyAttributeOutsideInit,SpellCheckingInspection
class RstCls:
	"""Rst commands group definition. 1 total commands, 0 Subgroups, 1 group commands"""

	def __init__(self, core: Core, parent):
		self._core = core
		self._cmd_group = CommandsGroup("rst", core, parent)

	def set(self) -> None:
		"""TRIGger:SBSW:SPI:RST \n
		Snippet: driver.trigger.sbsw.spi.rst.set() \n
		Presets the state of the selected frames and error types for the software trigger. \n
		"""
		self._core.io.write(f'TRIGger:SBSW:SPI:RST')

	def set_and_wait(self, opc_timeout_ms: int = -1) -> None:
		"""TRIGger:SBSW:SPI:RST \n
		Snippet: driver.trigger.sbsw.spi.rst.set_and_wait() \n
		Presets the state of the selected frames and error types for the software trigger. \n
		Same as set, but waits for the operation to complete before continuing further. Use the RsMxo.utilities.opc_timeout_set() to set the timeout value. \n
			:param opc_timeout_ms: Maximum time to wait in milliseconds, valid only for this call."""
		self._core.io.write_with_opc(f'TRIGger:SBSW:SPI:RST', opc_timeout_ms)
